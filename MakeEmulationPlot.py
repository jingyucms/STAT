import logging
import pickle
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
import joblib
from sklearn.gaussian_process import GaussianProcessRegressor as GPR
from sklearn.gaussian_process import kernels
from sklearn.preprocessing import StandardScaler

import src, sys
src.Initialize()

from src import design
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D 

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--Tag", help = "tag", type = str, default = "")
args = parser.parse_args()

AllDataTag = {}
with open('input/default_tag.p', 'rb') as handle:
    AllDataTag = pickle.load(handle)
tag = AllDataTag["tag"]
if args.Tag != "": tag = args.Tag 

import pickle
AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

Y = []
slices = {}
nobs = 0
for Item in AllData['data']['HeavyIon']['R_AA']:
    Y.append(AllData['model']['HeavyIon']['R_AA'][Item]['Y'])
    n = Y[-1].shape[1]
    slices[Item] = slice(nobs, nobs + n)
    nobs = nobs + n

Y = np.concatenate(Y, axis=1)

whichDesign = 105

figure0, axes0 = plt.subplots(figsize = (5, 5))
figure2, axes2 = plt.subplots(figsize = (5, 5))
axes0.plot(Y.T[:8, whichDesign], 'g')
axes2.plot(Y.T[:8, whichDesign], 'g')

SystemCount = len(AllData["systems"])
BinCount = len(AllData['observables'][0][1])

PCAIndex = range(Y.shape[0]) 
print("Y", Y.shape)

npc = 5

#------------------------STAT---------------------------

scaler = StandardScaler(copy=False)
pca = PCA(copy=False, svd_solver='full', whiten=True)  
Z = pca.fit_transform(scaler.fit_transform(Y))
Z = Z[:, :npc]
print("Z", Z.shape)


### JZ: If not whiten, transfer matrix should only be pca.compenents_
### JZ: see more: https://scikit-learn.org/dev/modules/generated/sklearn.decomposition.PCA.html
_trans_matrix = (
    pca.components_
    * np.sqrt(pca.explained_variance_[:, np.newaxis])  
    * scaler.scale_
)

A = _trans_matrix[:npc]
print("A", A.shape)

_var_trans = np.einsum(
    'ki,kj->kij', A, A, optimize=False).reshape(npc, nobs**2)

print("_var_trans", _var_trans.shape)

B = _trans_matrix[npc:]
_cov_trunc = np.dot(B.T, B)

_cov_trunc.flat[::nobs + 1] += 1e-4 * scaler.var_

X1 = np.dot(Z, A)
### JZ: If not whiten, use scaler.inverse_transform
X1 += scaler.mean_
#X1 = scaler.inverse_transform(X1)

cov = _cov_trunc[whichDesign]
cov = _cov_trunc.diagonal()
err = np.sqrt(cov)
axes0.errorbar(range(8), X1.T[:8, whichDesign], yerr=err[:8], fmt='bo')
figure0.savefig(f'result/{tag}/plots/testEmulation0.png', dpi = 192)

#------------------------STAT---------------------------

design = design.Design("HeavyIon")

ptp = design.max - design.min

ptp = ptp

noise0 = 0.5**2
noisemin = 0.0001**2
noisemax = 10**2

nu = 2.5

kernel = (kernels.RBF(
    length_scale = ptp,
    length_scale_bounds = np.outer(ptp, (0.01, 100)))
          + kernels.WhiteKernel(
              noise_level = noise0,
              noise_level_bounds = (noisemin, noisemax)))

alpha = 0.
nrestarts = 50

gps = [
    GPR(
        kernel=kernel, alpha=alpha,
        n_restarts_optimizer=nrestarts,
        copy_X_train=False
    ).fit(design, z)
    for z in Z.T
]

for n, (evr, gp) in enumerate(zip(
        pca.explained_variance_ratio_, gps
)):
    print(
        'GP {}: {:.5f} of variance, LML = {:.5g}, kernel: {}'
        .format(n, evr, gp.log_marginal_likelihood_value_, gp.kernel_)
    )

Examples = AllData["design"]
print("Examples", Examples.shape)
    
gp_mean = [gp.predict(Examples, return_cov=True) for gp in gps]
gp_mean, gp_cov = zip(*gp_mean)

gp_mean = np.array(gp_mean)
gp_cov = np.array(gp_cov)

gp_var = np.concatenate([
    c.diagonal()[:, np.newaxis] for c in gp_cov
], axis=1)

cov = np.dot(gp_var, _var_trans).reshape(gp_var.shape[0], nobs, nobs)

print(cov.shape, _cov_trunc.shape)
cov += _cov_trunc

mean = np.dot(gp_mean.T, A)
### JZ: If not whiten, use scaler.inverse_transform
mean += scaler.mean_
#mean = scaler.inverse_transform(mean)

cov = cov[whichDesign]
cov = cov.diagonal()
err = np.sqrt(cov)

axes2.errorbar(range(8), mean.T[:8, whichDesign], yerr=err[:8], fmt='bo')

custom_lines = [
    Line2D([0], [0], color='green', linestyle='-', linewidth=2, label="Prediction"),
    Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Emulated Prediction")
]
axes2.legend(handles=custom_lines, loc="upper right", frameon=False, handlelength=1, fontsize='small')

figure2.savefig(f'result/{tag}/plots/testEmulation2.png', dpi = 192)
