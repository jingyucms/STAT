import matplotlib.pyplot as plt
import numpy as np

import src
src.Initialize()
from src import mcmc
chain = mcmc.Chain()
MCMCSamples = chain.load()

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--Config', help = "config file", type = str, default = "")
args = parser.parse_args()

import yaml
if 'Config' in args:
    with open(args.Config, "r") as stream:
        try:
            Setup = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit()
else:
    Setup = {}

NDimension = len(AllData["labels"])
Ranges = np.array(AllData["ranges"]).T
# figure, axes = plt.subplots(figsize = (3 * NDimension, 3 * NDimension), ncols = NDimension, nrows = NDimension)

NFigure = NDimension
PanelList = range(0, NDimension)

if 'Reorder' in Setup:
    NFigure = len(Setup['Reorder'])
    PanelList = Setup['Reorder']


figure = plt.figure(figsize = (1.5 * (NFigure), 1.5 * (NFigure)))
gridspec = figure.add_gridspec(NFigure, NFigure, hspace = 0, wspace = 0)
axes = gridspec.subplots(sharex = 'col')
Names = AllData["labels"]

if 'Label' in Setup and len(Setup['Label']) >= len(Names):
    Names = Setup['Label']

Truth = np.full(NDimension, -999)
if 'holdoutdesign' in AllData:
    Truth = AllData['holdoutdesign'][0]

for i, row in enumerate(axes):
    for j, ax in enumerate(row):
        if i==j:
            ax.hist(MCMCSamples[:,PanelList[i]], bins=50,
                range=Ranges[:,PanelList[i]], histtype='step', color='green')
            ax.axvline(x = Truth[PanelList[i]], ymin = 0, color='red', linestyle='dotted', linewidth=5)
            ax.set_xlabel(Names[PanelList[j]])
            ax.set_xlim(*Ranges[:,PanelList[j]])
            ax.label_outer()
            ax.get_yaxis().set_ticks([])
            if 'Ticks' in Setup:
                ax.get_xaxis().set_ticks(Setup['Ticks'][PanelList[j]])
            if i == 0:
                ax.set_ylabel(Names[PanelList[j]])
        if i>j:
            ax.hist2d(MCMCSamples[:, PanelList[j]], MCMCSamples[:, PanelList[i]],
                bins=50, range=[Ranges[:,PanelList[j]], Ranges[:,PanelList[i]]],
                cmap='Greens')
            ax.scatter(Truth[PanelList[j]], Truth[PanelList[i]], s = 80, linewidths = 2.5, marker = 'o', facecolors = 'none', edgecolors = 'r')
            ax.set_xlabel(Names[PanelList[j]])
            ax.set_ylabel(Names[PanelList[i]])
            ax.set_xlim(*Ranges[:,PanelList[j]])
            ax.set_ylim(*Ranges[:,PanelList[i]])
            if 'Ticks' in Setup:
                ax.get_xaxis().set_ticks(Setup['Ticks'][PanelList[j]])
                ax.get_yaxis().set_ticks(Setup['Ticks'][PanelList[i]])
            ax.label_outer()
        if i<j:
            ax.axis('off')

Suffix = ''
if 'Suffix' in Setup:
    Suffix = '_' + Setup['Suffix']

plt.tight_layout()
tag = AllData['tag']
plt.savefig(f'result/{tag}/plots/Correlation{Suffix}.pdf', dpi = 192)
# plt.savefig(f'result/{tag}/plots/Correlation.png', dpi = 192)


