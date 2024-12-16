import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

import pickle

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--Alternate", help = "whether to plot a second collection", type = str, default = '')
parser.add_argument('--AlternateLabel', help = 'label for alternate collection', type = str, default = '')
parser.add_argument('--Tag', help = 'tag for the nominal', type = str, default = '')
parser.add_argument('--Suffix', help = 'suffix to add to file name', type = str, default = '')
args = parser.parse_args()

AllDataTag = {}
with open('input/default_tag.p', 'rb') as handle:
    AllDataTag = pickle.load(handle)
tag = AllDataTag["tag"]
if args.Tag != "": tag = args.Tag

AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

DoAlternate = False
if args.Alternate != '':
    DoAlternate = True

if args.Suffix != '':
    args.Suffix = '_' + args.Suffix

import src
src.Initialize()

from src import lazydict, emulator
Emulator = emulator.Emulator.from_cache('HeavyIon')

from src import mcmc
chain = mcmc.Chain(path = Path(f'result/{tag}/mcmc_chain.hdf'))
MCMCSamples = chain.load()

Examples = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 500), :]
TempPrediction = {"HeavyIon": Emulator.predict(Examples)}

if DoAlternate == True:
    chain = mcmc.Chain(path = Path(f'result/{args.Alternate}/mcmc_chain.hdf'))
    MCMCSamples2 = chain.load()
    Examples2 = MCMCSamples2[ np.random.choice(range(len(MCMCSamples2)), 500), :]
    TempPrediction2 = {"HeavyIon": Emulator.predict(Examples2)}

SystemCount = len(AllData["systems"])
BinCount = len(AllData['observables'][0][1])

#RC = int(np.sqrt(BinCount))
#CC = int(np.ceil(BinCount / RC))

CC = 10
RC = int(np.ceil(BinCount / CC))

figure, axes = plt.subplots(figsize = (3 * CC, 3 * RC), nrows = RC, ncols = CC)

for s2 in range(0, RC * CC):
    ax = int(np.floor(s2 / CC))
    ay = s2 % CC
    axes[ax][ay].set_xlabel(r"$p_{T}$")
    axes[ax][ay].set_ylabel(r"$R_{AA}$")

    if s2 >= BinCount:
        axes[ax][ay].axis('off')
        continue

    S1 = AllData["systems"][0]
    O  = AllData["observables"][0][0]
    S2 = AllData["observables"][0][1][s2]

    if "JetDz" in S2 and "ATLAS" in S2:
        axes[ax][ay].set_xlabel(r"z")
    elif "JetDz" in S2 and "CMS" in S2:
        axes[ax][ay].set_xlabel(r"ln(1/z)")
    elif "Tg" in S2:
        axes[ax][ay].set_xlabel(r"$\theta_{g}$")
    elif "Zg" in S2:
        axes[ax][ay].set_xlabel(r"$z_{g}$")
    else:
        axes[ax][ay].set_xlabel(r"$p_{T}$")

    DX = AllData["data"][S1][O][S2]['x']
    DY = AllData["data"][S1][O][S2]['y']
    try: 
        DE = np.sqrt(AllData["data"][S1][O][S2]['yerr']['stat'][:,0]**2 + AllData["data"][S1][O][S2]['yerr']['sys'][:,0]**2)
    except KeyError:
        DE = np.sqrt(AllData["data"][S1][O][S2]['yerr']['sum'][:,0]**2)

    t = AllData["observables"][0][1][s2].replace('Inclusive','').split('_')
    title = '{}_{}\n{}_{}_{}'.format(t[0],t[1],t[2],t[3],t[4])
    #axes[ax][ay].set_title(AllData["observables"][0][1][s2])
    # axes[ax][ay].set_xscale('log')
    axes[ax][ay].set_title(title)
    
    axes[ax][ay].set_ylim(0, 2)
    if len(DX) > 1:
        axes[ax][ay].plot([DX[0], DX[-1]], [1, 1], 'k-.')
    else:
        axes[ax][ay].plot([np.floor(DX[0] * 0.9), np.ceil(DX[0] * 1.1)], [1, 1], 'k-.')

    if DoAlternate == False:
        for i, y in enumerate(TempPrediction[S1][O][S2]):
            if len(DX) > 1:
                axes[ax][ay].plot(DX, y, 'b-', alpha=0.05, label="Nominal" if i==0 else '')
            else:
                axes[ax][ay].plot([np.floor(DX[0] * 0.9), np.ceil(DX[0] * 1.1)], [y[0], y[0]], 'b-', alpha=0.025, label = 'Nominal' if i == 0 else '')
    if DoAlternate == True:
        for i, y in enumerate(TempPrediction2[S1][O][S2]):
            if len(DX) > 1:
                axes[ax][ay].plot(DX, y, 'g-', alpha=0.05, label=args.AlternateLabel if i==0 else '')
            else:
                axes[ax][ay].plot([np.floor(DX[0] * 0.9), np.ceil(DX[0] * 1.1)], [y[0], y[0]], 'g-', alpha=0.025, label = 'Nominal' if i == 0 else '')
    axes[ax][ay].errorbar(DX, DY, yerr = DE, fmt='ro', label="Measurements")
    axes[ax][ay].set_xscale('log')

plt.tight_layout()
tag = AllData['tag']
figure.savefig(f'result/{tag}/plots/ObservablePosterior{args.Suffix}.pdf', dpi = 192)
figure.savefig(f'result/{tag}/plots/ObservablePosterior{args.Suffix}.png', dpi = 192)
# figure.savefig(f'result/{tag}/plots/ObservablePosterior.png', dpi = 192)


