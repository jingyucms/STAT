import matplotlib.pyplot as plt
import numpy as np
import yaml
from pathlib import Path

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--Config", help = "plot configuration file", type = str, default = "yaml/PlotConfig.yaml")
parser.add_argument("--Alternate", help = "whether to plot a second collection", type = str, default = '')
parser.add_argument('--AlternateLabel', help = 'label for alternate collection', type = str, default = '')
parser.add_argument('--Suffix', help = 'suffix to add to file name', type = str, default = '')
args = parser.parse_args()

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
chain = mcmc.Chain()
MCMCSamples = chain.load()

Examples = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 500), :]
TempPrediction = {"HeavyIon": Emulator.predict(Examples)}

if DoAlternate == True:
    chain = mcmc.Chain(path = Path(f'result/{args.Alternate}/mcmc_chain.hdf'))
    MCMCSamples2 = chain.load()
    Examples2 = MCMCSamples2[ np.random.choice(range(len(MCMCSamples2)), 500), :]
    TempPrediction2 = {"HeavyIon": Emulator.predict(Examples2)}

def MakePlot(ToPlot, Suffix, Label, Common):
    # Let's not remove things silently.  We should let fails fail for this
    # ToPlot = [x for x in ToPlot if x in AllData["observables"][0][1]]

    if Suffix != "":
        Suffix = "_" + Suffix

    if len(ToPlot) == 0:
        print("Nothing valid specified")
        return

    SystemCount = len(AllData["systems"])
    BinCount = len(ToPlot)

    figure = plt.figure(figsize = (3 * BinCount + 1, 3 + 1))
    gridspec = figure.add_gridspec(1, BinCount, hspace = 0, wspace = 0)
    axes = gridspec.subplots(sharex = 'col', sharey = 'row')

    if BinCount == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        ax.set_xlabel(r"$p_{T}$", fontsize = 15)
        ax.set_ylabel(r"$R_{AA}$", fontsize = 15)

        S1 = AllData["systems"][0]
        O  = AllData["observables"][0][0]
        S2 = ToPlot[i]

        if i < len(Label):
            ax.text(0.05, 0.95, Label[i],
                verticalalignment='top', horizontalalignment='left',
                transform = ax.transAxes, fontsize = 15)

        ax.set_ylim([0, 1.2])
        ax.label_outer()

        if S2 not in AllData["data"][S1][O]:
            continue

        DX = AllData["data"][S1][O][S2]['x']
        DY = AllData["data"][S1][O][S2]['y']
        DE = np.sqrt(AllData["data"][S1][O][S2]['yerr']['stat'][:,0]**2 + AllData["data"][S1][O][S2]['yerr']['sys'][:,0]**2)

        if DoAlternate == True:
            for j, y in enumerate(TempPrediction2[S1][O][S2]):
                if len(DX) > 1:
                    ax.plot(DX, y, 'g-', alpha=0.05, label = args.AlternateLabel if j == 0 else '')
                else:
                    ax.plot([np.floor(DX[0] * 0.9), np.ceil(DX[0] * 1.1)], [y[0], y[0]], 'g-', alpha=0.05, label = args.AlternateLabel if j == 0 else '')
        else:
            for j, y in enumerate(TempPrediction[S1][O][S2]):
                if len(DX) > 1:
                    ax.plot(DX, y, 'b-', alpha=0.025, label = 'Nominal' if j == 0 else '')
                else:
                    ax.plot([np.floor(DX[0] * 0.9), np.ceil(DX[0] * 1.1)], [y[0], y[0]], 'b-', alpha=0.025, label = 'Nominal' if j == 0 else '')
        ax.errorbar(DX, DY, yerr = DE, fmt='ro')

    axes[0].set_title(Common, loc = 'left', fontsize = 15)
    axes[len(axes)-1].legend(loc = 'upper right')

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/SmallObservablePosterior{args.Suffix}{Suffix}.pdf', dpi = 192)
    plt.close('all')


with open(args.Config, 'r') as stream:
    try:
        setup = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

for item in setup['ObservablePlot']:
    MakePlot(item['Key'], item['Suffix'], item['Label'], item['Common'])







