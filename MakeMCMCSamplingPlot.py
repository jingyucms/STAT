import matplotlib.pyplot as plt
from pathlib import Path

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--Config', help = "config file", type = str, default = "")
parser.add_argument('--Tag', help = "config file", type = str, default = "")
args = parser.parse_args()

import pickle
AllDataTag = {}
with open('input/default_tag.p', 'rb') as handle:
    AllDataTag = pickle.load(handle)
tag = AllDataTag["tag"]
if args.Tag != "": tag = args.Tag

import src
src.Initialize()
from src import mcmc
chain = mcmc.Chain(path = Path(f'result/{tag}/mcmc_chain.h5'))
MCMCSamples = chain.load()

import pickle
AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

with chain.dataset() as d:
    W = d.shape[0]     # number of walkers
    S = d.shape[1]     # number of steps
    N = d.shape[2]     # number of paramters
    T = int(S / 100)   # "thinning"
    A = 20 / W

    I = W/20   # number of walkers to plot

    print("Number of walkers:", W)
    print("Number of steps:", S)
    print("Number of paramters:", N)
    
    figure, axes = plt.subplots(figsize = (18, 2 * N), ncols = 1, nrows = N)
    for i, ax in enumerate(axes):
        for j in range(0, W):
            ax.plot(range(0, S, T), d[j, ::T, i], alpha = A)
            #ax[0].plot(range(0, S, T), d[j, ::T, i])
        #ax[1].hist(d[82, :, i], bins=50)
    plt.tight_layout()
    tag = AllData['tag']
    plt.savefig(f'result/{tag}/plots/MCMCSamples.pdf', dpi = 192)
