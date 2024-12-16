"""
Markov chain Monte Carlo model calibration using the `affine-invariant ensemble
sampler (emcee) <http://dfm.io/emcee>`_.

This module must be run explicitly to create the posterior distribution.
Run ``python -m src.mcmc --help`` for complete usage information.

On first run, the number of walkers and burn-in steps must be specified, e.g.
::

    python -m src.mcmc --nwalkers 500 --nburnsteps 100 200

would run 500 walkers for 100 burn-in steps followed by 200 production steps.
This will create the HDF5 file :file:`cache/mcmc_chain.hdf` (default path).

On subsequent runs, the chain resumes from the last point and the number of
walkers is inferred from the chain, so only the number of production steps is
required, e.g. ::

    python -m src.mcmc 300

would run an additional 300 production steps (total of 500).

To restart the chain, delete (or rename) the chain HDF5 file.
"""

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
from . import log_posterior

class LoggingEnsembleSampler(emcee.EnsembleSampler):
    def run_mcmc(self, X0, nsteps, status=None, **kwargs):
        """
        Run MCMC with logging every 'status' steps (default: approx 10% of
        nsteps).

        """
        #logging.info('running %d walkers for %d steps', self.k, nsteps)
        
        logging.info('running %d steps', nsteps)

        if status is None:
            status = nsteps // 10

        for n, result in enumerate(
                self.sample(X0, iterations=nsteps, **kwargs),
                start=1
        ):
            if n % status == 0 or n == nsteps:
                af = self.acceptance_fraction
                logging.info(
                    'step %d: acceptance fraction: '
                    'mean %.4f, std %.4f, min %.4f, max %.4f',
                    n, af.mean(), af.std(), af.min(), af.max()
                )

        return result
                        
    
class Chain:
    """
    High-level interface for running MCMC calibration and accessing results.

    Currently all design parameters except for the normalizations are required
    to be the same at all beam energies.  It is assumed (NOT checked) that all
    system designs have the same parameters and ranges (except for the norms).

    """
    def __init__(self, path=workdir / 'cache' / 'mcmc_chain.h5'):
        self.path = path
        self.path.parent.mkdir(exist_ok=True)

        # parameter order:
        #  - normalizations (one for each system)
        #  - all other physical parameters (same for all systems)
        #  - model sys error
        """
        def keys_labels_range():
            for sys in systems:
                d = Design(sys)
                klr = zip(d.keys, d.labels, d.range)
                k, l, r = next(klr)
                #assert k == 'lambda_jet'
                yield (
                    '{} {}'.format(k, sys),
                    '{}\n{:.2f} TeV'.format(l, d.beam_energy/1000),
                    r
                )

            yield from klr
        """

        def keys_labels_range():
            d = Design(systems[0])
            klr = zip(d.keys, d.labels, d.range)
            
            yield from klr

        self.keys, self.labels, self.range = map(list, zip(*keys_labels_range()))
        self.ndim = len(self.range)
        self.min, self.max = map(np.array, zip(*self.range))

    def random_pos(self, n=1):
        """
        Generate `n` random positions in parameter space.

        """
        return np.random.uniform(self.min, self.max, (n, self.ndim))

    @staticmethod
    def map(f, args):
        """
        Dummy function so that this object can be used as a 'pool' for
        :meth:`emcee.EnsembleSampler`.

        """
        return f(args)

    def run_mcmc(self, nsteps, nburnsteps=None, nwalkers=None, status=None, model_cov_modifier=None, model_cov_factor=None, likelihood_type=None, data_c_factor=0):
        """
        Run MCMC model calibration.  If the chain already exists, continue from
        the last point, otherwise burn-in and start the chain.

        """
        
#        with self.open('a') as f:
#            try:
#                dset = f['chain']
#            except KeyError:
#                burn = True
#                if nburnsteps is None or nwalkers is None:
#                    logging.error(
#                        'must specify nburnsteps and nwalkers to start chain'
#                    )
#                    return
#                dset = f.create_dataset(
#                    'chain', dtype='f8',
#                    shape=(nwalkers, 0, self.ndim),
#                    chunks=(nwalkers, 1, self.ndim),
#                    maxshape=(nwalkers, None, self.ndim),
#                    compression='lzf'
#                )
#            else:
#                burn = False
#                nwalkers = dset.shape[0]

        #try:
        #    f = self.open('a')
        #    dset = f['chain']
        #    burn = False
        #except KeyError:
        #    burn = True    


        slices = {}
        my_expt_y = {}
        my_expt_c = {}
        my_expt_cov = {}

        for sys, sysdata in exp_data_list.items():
            nobs = 0

            slices[sys] = []
            
            for obs, subobslist in observables:
                try:
                    obsdata = sysdata[obs]
                except KeyError:
                    continue
    
                for subobs in subobslist:
                    try:
                        dset = obsdata[subobs]
                    except KeyError:
                        continue
    
                    n = dset['y'].size
                    slices[sys].append(
                        (obs, subobs, slice(nobs, nobs + n))
                    )
                    nobs += n
    
            my_expt_y[sys] = np.zeros(nobs)
            my_expt_c[sys] = np.zeros(nobs)
            my_expt_cov[sys] = np.zeros((nobs, nobs))
    
            for obs1, subobs1, slc1 in slices[sys]:
                #self._expt_y[sys][slc1] = exp_data_list[sys][obs1][subobs1]['y']
                my_expt_y[sys][slc1] = exp_data_list[sys][obs1][subobs1]['y']
                if 'c' in exp_data_list[sys][obs1][subobs1]:
                    my_expt_c[sys][slc1] = float(exp_data_list[sys][obs1][subobs1]['c'])
                if exp_cov is None:
                    for obs2, subobs2, slc2 in slices[sys]:
                        my_expt_cov[sys][slc1, slc2] = cov(
                            sys, obs1, subobs1, obs2, subobs2
                        )
                        
    
            #Allows user to specify experimental covariance matrix in __init__.py
            if exp_cov is not None:
                for obs1, subobs1, slc1 in slices[sys]:
                    for obs2, subobs2, slc2 in slices[sys]:
                        if exp_cov[sys][(obs1, subobs1)][(obs2, subobs2)] is not None:
                            my_expt_cov[sys][slc1, slc2] = exp_cov[sys][(obs1, subobs1)][(obs2, subobs2)]
        
        burn = True
        
        start = time.time()

        #log_posterior.init_var(my_expt_y, my_expt_c, my_expt_cov, emulators, slices, observables, self.ndim, self.min, self.max)
        p0 = self.random_pos(nwalkers)

        ctx = multiprocessing.get_context('spawn')
        with ctx.Pool(initializer=log_posterior.init_var, initargs=[my_expt_y, my_expt_c, my_expt_cov, emulators, slices, observables, self.ndim, self.min, self.max], processes=12) as pool:
        #if True:
            
            nburn0 = nburnsteps // 2

            sampler = LoggingEnsembleSampler(
                nwalkers, self.ndim, log_posterior.log_posterior, pool=pool,
                #moves=[
                #    (emcee.moves.DEMove(), 0.8),
                #    (emcee.moves.DESnookerMove(), 0.2),
                #],
            )

            if burn:
                logging.info(
                    'no existing chain found, starting initial burn-in')
                # Run first half of burn-in starting from random positions.
                sampler.run_mcmc(
                    p0,
                    nburn0,
                    status=status
                )
                logging.info('resampling walker positions')

                #sys.exit()
                # Reposition walkers to the most likely points in the chain,
                # then run the second half of burn-in.  This significantly
                # accelerates burn-in and helps prevent stuck walkers.
                X0 = sampler.flatchain[
                    np.unique(
                        sampler.flatlnprobability,
                        return_index=True
                    )[1][-nwalkers:]
                ]
                
                sampler.reset()
                X0 = sampler.run_mcmc(
                    X0,
                    nburnsteps - nburn0,
                    status=status
                )[0]
                sampler.reset()
                logging.info('burn-in complete, starting production')
            else:
                logging.info('restarting from last point of existing chain')
                X0 = dset[:, -1, :]
  
            sampler.run_mcmc(X0, nsteps, status=status)

            try:
                autocorr_time = sampler.get_autocorr_time()
            except emcee.autocorr.AutocorrError as e:
                print(f"Autocorrelation time could not be reliably estimated: {e}")
                # Handle the case, perhaps use a default value or continue with a warning
                autocorr_time = None
            except Exception as e:
                print(f"An error occurred: {e}")
                autocorr_time = None

            if autocorr_time is not None:
                print(f"Estimated autocorrelation time: {autocorr_time}")
            else:
                print("Proceeding with default behavior due to autocorrelation estimation issue.")

            end = time.time()

            logging.info('processing time: %s seconds', end - start)
            logging.info('writing chain to file')
            #dset.resize(dset.shape[1] + nsteps, 1)
            #dset[:, -nsteps:, :] = sampler.chain

            with self.open('a') as f:
                dset = f.create_dataset(
                    'chain', dtype='f8',
                    shape=(nwalkers, 0, self.ndim),
                    chunks=(nwalkers, 1, self.ndim),
                    maxshape=(nwalkers, None, self.ndim),
                    compression='lzf'
                )
                dset.resize(dset.shape[1] + nsteps, 1)
                dset[:, -nsteps:, :] = sampler.chain
            #with open(str(self.path), 'wb') as f:
            #    data_to_pickle = {
            #        'chain': sampler.chain,
            #        'lnprobability': sampler.lnprobability,
            #        'blobs': sampler.blobs,
            #    }
            #    pickle.dump(data_to_pickle, f)

            logging.info('Done.')   

    def open(self, mode='r'):
        """
        Return a handle to the chain HDF5 file.

        """
        return h5py.File(str(self.path), mode)

    @contextmanager
    def dataset(self, mode='r', name='chain'):
        """
        Context manager for quickly accessing a dataset in the chain HDF5 file.

        >>> with Chain().dataset() as dset:
                # do something with dset object

        """
        with self.open(mode) as f:
            yield f[name]

    def load(self, *keys, thin=1):
        """
        Read the chain from file.  If `keys` are given, read only those
        parameters.  Read only every `thin`'th sample from the chain.

        """
        if keys:
            indices = [self.keys.index(k) for k in keys]
            ndim = len(keys)
            if ndim == 1:
                indices = indices[0]
        else:
            ndim = self.ndim
            indices = slice(None)

        with self.dataset() as d:
            return np.array(d[:, ::thin, indices]).reshape(-1, ndim)

#     def samples(self, n=1):
#         """
#         Predict model output at `n` parameter points randomly drawn from the
#         chain.
# 
#         """
#         with self.dataset() as d:
#             X = np.array([
#                 d[i] for i in zip(*[
#                     np.random.randint(s, size=n) for s in d.shape[:2]
#                 ])
#             ])
# 
#         #return self._predict(X)
#         return predict(X)


def credible_interval(samples, ci=.9):
    """
    Compute the highest-posterior density (HPD) credible interval (default 90%)
    for an array of samples.

    """
    # number of intervals to compute
    nci = int((1 - ci)*samples.size)

    # find highest posterior density (HPD) credible interval
    # i.e. the one with minimum width
    argp = np.argpartition(samples, [nci, samples.size - nci])
    cil = np.sort(samples[argp[:nci]])   # interval lows
    cih = np.sort(samples[argp[-nci:]])  # interval highs
    ihpd = np.argmin(cih - cil)

    return cil[ihpd], cih[ihpd]


def main():
    parser = argparse.ArgumentParser(description='Markov chain Monte Carlo')

    parser.add_argument(
        'nsteps', type=int,
        help='number of steps'
    )
    parser.add_argument(
        '--nwalkers', type=int,
        help='number of walkers'
    )
    parser.add_argument(
        '--nburnsteps', type=int,
        help='number of burn-in steps'
    )
    parser.add_argument(
        '--status', type=int,
        help='number of steps between logging status'
    )
    parser.add_argument(
        '--model_cov_modifier', type=float, default=1.00,
        help='model cov modifier'
    )
    parser.add_argument(
        '--model_cov_factor', type=float, default=1.00,
        help='model cov factor'
    )
    parser.add_argument(
        '--likelihood_type', type=int, default=0,
        help='type of likelihood.  0 = mvn, 1 = d^2, 2 = chi^2, 3 = chi^2 with correlated error'
    )
    parser.add_argument(
        '--data_c_factor', type=float, default=0.00,
        help='multiplicative factor for selected data points'
    )

    args = parser.parse_args()
    
    #initGlobalVar()
    log_posterior.set_mcmc_variables(model_cov_modifier = args.model_cov_modifier,
                                     model_cov_factor = args.model_cov_factor,
                                     likelihood_type = args.likelihood_type,
                                     data_c_factor = args.data_c_factor)
    Chain().run_mcmc(**vars(parser.parse_args()))


if __name__ == '__main__':
    main()
