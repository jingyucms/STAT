import logging
import pickle
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
import joblib
from sklearn.gaussian_process import GaussianProcessRegressor as GPR
from sklearn.gaussian_process import kernels
from sklearn.preprocessing import StandardScaler

import src
src.Initialize()
#import cachedir, lazydict, observables, data_list#model
#from design import Design
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

figure1, axes1 = plt.subplots(figsize = (5, 5))
figure2, axes2 = plt.subplots(figsize = (5, 5))
axes1.plot(Y.T[:10, whichDesign], 'g')
axes2.plot(Y.T[:10, whichDesign], 'g')

SystemCount = len(AllData["systems"])
BinCount = len(AllData['observables'][0][1])

#def ReduceDimension(Data, NPC, Slices):
#    scaler = StandardScaler(copy = True)
#    pca = PCA(n_components = NPC, copy = True, whiten = True, svd_solver = 'full')
#    #pca = PCA(copy = True, whiten = True, svd_solver = 'full')
#    Y = pca.fit_transform(scaler.fit_transform(Data))
#    #print(Data.shape, Y.shape)
#    XTemp = pca.inverse_transform(Y) * scaler.scale_ + scaler.mean_
#    return {"R_AA": {Item: XTemp[..., S] for Item, S in Slices.items()}}


npc = 5

scaler = StandardScaler(copy=False)

pca = PCA(copy=False, whiten=True, svd_solver='full')

PCAIndex = range(Y.shape[0])
PCAY = np.array([Y[i] for i in PCAIndex])
print("PCAIndex", PCAIndex)
print("PCAY", PCAY.shape)

pca.fit_transform(scaler.fit_transform(PCAY))

Z = pca.transform(scaler.transform(Y))

Z = Z[:, :npc]
print("Z", Z.shape)

_trans_matrix = (
    pca.components_
    * np.sqrt(pca.explained_variance_[:, np.newaxis])
    * scaler.scale_
)


A = _trans_matrix[:npc]
print("A", A.shape)

_var_trans = np.einsum(
    'ki,kj->kij', A, A, optimize=False).reshape(npc, nobs**2)

B = _trans_matrix[npc:]
_cov_trunc = np.dot(B.T, B)

_cov_trunc.flat[::nobs + 1] += 1e-4 * scaler.var_

#print(Z[:,0].shape, A[0].shape)
#print(Z[:,0].shape, A[1].shape)

X1 = np.dot(Z[:,0].reshape(Z[:,0].shape[0], 1), A[0].reshape(1, A[0].shape[0]))
X1 += scaler.mean_
X2 = np.dot(Z[:,1].reshape(Z[:,1].shape[0], 1), A[1].reshape(1, A[1].shape[0]))
X2 += scaler.mean_

axes1.plot(X1.T[:10, whichDesign], 'b')
axes1.plot(X2.T[:10, whichDesign], 'b')

figure1.savefig(f'result/{tag}/plots/testEmulation.png', dpi = 192)

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

#kernel = (kernels.Matern(
#    length_scale = ptp,
#    length_scale_bounds = np.outer(ptp, (0.01, 100)),
#    nu = nu)
#          + kernels.WhiteKernel(
#              noise_level = noise0,
#              noise_level_bounds = (noisemin, noisemax)))

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

print('{} PCs explain {:.5f} of variance'.format(
    npc,
    pca.explained_variance_ratio_.sum()
))

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

print(np.array(gp_mean).shape)
print(np.array(gp_cov).shape)
gp_mean = np.array(gp_mean)
gp_cov = np.array(gp_cov)

gp_var = np.concatenate([
    c.diagonal()[:, np.newaxis] for c in gp_cov
], axis=1)

cov = np.dot(gp_var, _var_trans).reshape(gp_var.shape[0], nobs, nobs)

#print(gp_var.shape, _var_trans.shape)
print(cov.shape, _cov_trunc.shape)
cov += _cov_trunc

mean = np.dot(gp_mean.T, A)
mean += scaler.mean_

cov = cov[whichDesign]
cov = cov.diagonal()
print(cov.shape)
err = np.sqrt(cov)

#axes2.plot(mean.T[:10, whichDesign], 'b')
#print(len(range(10)))
axes2.errorbar(range(10), mean.T[:10, whichDesign], yerr=err[:10], fmt='bo')

custom_lines = [
    Line2D([0], [0], color='green', linestyle='-', linewidth=2, label="Prediction"),
    Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Emulated Prediction")
]
axes2.legend(handles=custom_lines, loc="upper right", frameon=False, handlelength=1, fontsize='small')

figure2.savefig(f'result/{tag}/plots/testEmulation2.png', dpi = 192)
