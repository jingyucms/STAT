import argparse,sys
from contextlib import contextmanager
import logging

import emcee
import h5py
import numpy as np
from scipy.linalg import lapack
import joblib
from . import workdir, systems, observables, exp_data_list, exp_cov#, expt
from .design import Design
from .emulator import emulators
import pickle
from scipy.stats import multivariate_normal
from operator import add
#from multiprocessing import Pool
import multiprocessing
import time


def cov(
        system, obs1, subobs1, obs2, subobs2,
        stat_frac=1e-4, sys_corr_length=100, cross_factor=.8,
        corr_obs={
            frozenset({'dNch_deta', 'dET_deta', 'dN_dy'}),
        }
):
    """
    Estimate a covariance matrix for the given system and pair of observables,
    e.g.:

    >>> cov('PbPb2760', 'dN_dy', 'pion', 'dN_dy', 'pion')
    >>> cov('PbPb5020', 'dN_dy', 'pion', 'dNch_deta', None)

    For each dataset, stat and sys errors are used if available.  If only
    "summed" error is available, it is treated as sys error, and `stat_frac`
    sets the fractional stat error.

    Systematic errors are assumed to have a Gaussian correlation as a function
    of centrality percentage, with correlation length set by `sys_corr_length`.

    If obs{1,2} are the same but subobs{1,2} are different, the sys error
    correlation is reduced by `cross_factor`.

    If obs{1,2} are different and uncorrelated, the covariance is zero.  If
    they are correlated, the sys error correlation is reduced by
    `cross_factor`.  Two different obs are considered correlated if they are
    both a member of one of the groups in `corr_obs` (the groups must be
    set-like objects).  By default {Nch, ET, dN/dy} are considered correlated
    since they are all related to particle / energy production.

    """
    def unpack(obs, subobs):
        dset = exp_data_list[system][obs][subobs]
        yerr = dset['yerr']

        try:
            stat = yerr['stat']
            sys = yerr['sys']
        except KeyError:
            stat = dset['y'] * stat_frac
            sys = yerr['sum']

        return dset['x'], stat, sys

    x1, stat1, sys1 = unpack(obs1, subobs1)
    x2, stat2, sys2 = unpack(obs2, subobs2)

    if obs1 == obs2:
        same_obs = (subobs1 == subobs2)
    else:
        # check if obs are both in a correlated group
        if any({obs1, obs2} <= c for c in corr_obs):
            same_obs = False
        else:
            return np.zeros((x1.size, x2.size))

    # compute the sys error covariance
    C = (
        np.exp(-.5*(np.subtract.outer(x1, x2)/sys_corr_length)**2) *
        np.outer(sys1, sys2)
    )

    if same_obs:
        # add stat error to diagonal
        C.flat[::C.shape[0]+1] += stat1**2
    else:
        # reduce correlation for different observables
        C *= cross_factor

    return C

def mvn_loglike(y, cov):
    """
    Evaluate the multivariate-normal log-likelihood for difference vector `y`
    and covariance matrix `cov`:

        log_p = -1/2*[(y^T).(C^-1).y + log(det(C))] + const.

    The likelihood is NOT NORMALIZED, since this does not affect MCMC.  The
    normalization const = -n/2*log(2*pi), where n is the dimensionality.

    Arguments `y` and `cov` MUST be np.arrays with dtype == float64 and shapes
    (n) and (n, n), respectively.  These requirements are NOT CHECKED.

    The calculation follows algorithm 2.1 in Rasmussen and Williams (Gaussian
    Processes for Machine Learning).

    """
    # Compute the Cholesky decomposition of the covariance.
    # Use bare LAPACK function to avoid scipy.linalg wrapper overhead.
    L, info = lapack.dpotrf(cov, clean=False)

    if info < 0:
        raise ValueError(
            'lapack dpotrf error: '
            'the {}-th argument had an illegal value'.format(-info)
        )
    elif info < 0:
        raise np.linalg.LinAlgError(
            'lapack dpotrf error: '
            'the leading minor of order {} is not positive definite'
            .format(info)
        )

    # Solve for alpha = cov^-1.y using the Cholesky decomp.
    alpha, info = lapack.dpotrs(L, y)

    if info != 0:
        raise ValueError(
            'lapack dpotrs error: '
            'the {}-th argument had an illegal value'.format(-info)
        )

    return -.5*np.dot(y, alpha) - np.log(L.diagonal()).sum()

def mvd_loglike(y, cov):
    """
    Just Distance^2
    """
    return -0.5 * np.dot(y, y)

def mvc_loglike(y, cov):
    """
    Chi^2 without correlations
    """
    dy = y / np.sqrt(cov.diagonal())
    return -0.5 * np.dot(dy, dy)

def mcc_loglike(y, cov):
    """
    Chi^2 with correlations taken into account
    Evaluates y^T C^-1 y
    See mvn_loglike for explanation on method
    """
    # Compute the Cholesky decomposition of the covariance.
    # Use bare LAPACK function to avoid scipy.linalg wrapper overhead.
    L, info = lapack.dpotrf(cov, clean=False)

    if info < 0:
        raise ValueError(
            'lapack dpotrf error: '
            'the {}-th argument had an illegal value'.format(-info)
        )
    elif info < 0:
        raise np.linalg.LinAlgError(
            'lapack dpotrf error: '
            'the leading minor of order {} is not positive definite'
            .format(info)
        )

    # Solve for alpha = cov^-1.y using the Cholesky decomp.
    alpha, info = lapack.dpotrs(L, y)

    if info != 0:
        raise ValueError(
            'lapack dpotrs error: '
            'the {}-th argument had an illegal value'.format(-info)
        )

    return np.dot(y, alpha)

def loglike(y, cov, t):
    if t == 1:
        return mvd_loglike(y, cov)
    elif t == 2:
        return mvc_loglike(y, cov)
    elif t == 3:
        return mcc_loglike(y, cov)
    return mvn_loglike(y, cov)

model_cov_modifier = 1.
model_cov_factor = 1.
likelihood_type = 0.
data_c_factor = 0.
def set_mcmc_variables(model_cov_modifier=1.00, model_cov_factor=1.00, likelihood_type=0, data_c_factor=0.00):
    model_cov_modifier = model_cov_modifier
    model_cov_factor = model_cov_factor
    likelihood_type = likelihood_type
    data_c_factor = data_c_factor

_expt_y = {}
_expt_c = {}
_expt_cov = {}
_emulators = None
_slices = {}
_emulators = None
_observables = None
_ndim = None
_min = None
_max = None
def init_var(expt_y, expt_c, expt_cov, emulators, slices, observables, ndim, min, max) ->None:
    global _expt_y
    global _expt_c
    global _expt_cov
    global _emulators
    global _slices
    global _observables
    global _ndim
    global _min
    global _max
    _expt_y = expt_y
    _expt_c = expt_c
    _expt_cov = expt_cov
    _emulators = emulators
    _slices = slices
    _observables = observables
    _ndim = ndim
    _min = min
    _max = max

# def predict(X, **kwargs):
#     """
#     Call each system emulator to predict model output at X.
# 
#     """
#     return {
#         sys: emulators[sys].predict(
#             X[:, ],#[n] + self._common_indices],
#             **kwargs
#         )
#         for n, sys in enumerate(systems)
#     }


def log_posterior(X, extra_std_prior_scale=0.25, model_sys_error = False):
    """
    Evaluate the posterior at `X`.

    `extra_std_prior_scale` is the scale parameter for the prior
    distribution on the model sys error parameter:

        prior ~ sigma^2 * exp(-sigma/scale)

    This model sys error parameter is not by default implemented.

    """

    X = np.array(X, copy=False, ndmin=2)
    lp = np.zeros(X.shape[0])

    inside = np.all((X > _min) & (X < _max), axis=1)
    lp[~inside] = -np.inf

    nsamples = np.count_nonzero(inside)

    if nsamples > 0:
        if model_sys_error:
            extra_std = X[inside, -1]
        else:
            extra_std = 0.0

        pred =  {
            sys: _emulators[sys].predict(
                X[:, ],#[n] + self._common_indices],
                return_cov=True,
                extra_std=extra_std
            )
            for n, sys in enumerate(systems)
        }
        for sys in systems:
            nobs = _expt_y[sys].size
            # allocate difference (model - expt) and covariance arrays
            dY = np.zeros((nsamples, nobs))
            cov1 = np.zeros((nsamples, nobs, nobs))
            cov0 = np.zeros((nsamples, nobs, nobs))
            ltype = np.full(nsamples, likelihood_type)

            model_Y, model_cov = pred[sys]

            # copy predictive mean and covariance into allocated arrays
            #for obs1, subobs1, slc1 in self._slices[sys]:
            for obs1, subobs1, slc1 in _slices[sys]:
                dY[:, slc1] = model_Y[obs1][subobs1]
                for obs2, subobs2, slc2 in _slices[sys]:
                    cov1[:, slc1, slc2] += model_cov[(obs1, subobs1), (obs2, subobs2)] * model_cov_modifier


            dY[:] = _expt_y[sys] * (1 + data_c_factor * _expt_c[sys]) - dY[:]

            cov1[:] += _expt_cov[sys]
            cov0[:] += _expt_cov[sys]

            # compute log likelihood at each point
            if model_cov_factor == 1:
                lp[inside] += list(map(loglike, dY, cov1, ltype))
            elif model_cov_factor == 0:
                lp[inside] += list(map(loglike, dY, cov0, ltype))
            else:
                lp[inside] += list(map(add,
                    list([x * model_cov_factor for x in list(map(loglike, dY, cov1, ltype))]),
                    list([x * (1 - model_cov_factor) for x in list(map(loglike, dY, cov0, ltype))])))

        # add prior for extra_std (model sys error)
        if model_sys_error:
            lp[inside] += 2*np.log(extra_std) - extra_std / extra_std_prior_scale

    return lp
