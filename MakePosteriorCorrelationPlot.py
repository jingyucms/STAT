import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D 

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--Alternate", help = "whether to plot a second collection", type = str, default = '')
parser.add_argument("--NominalLabel", help = "label for the nominal", type = str, default = '')
parser.add_argument('--AlternateLabel', help = 'label for alternate collection', type = str, default = '')
parser.add_argument('--Config', help = 'config file', type = str, default = '')
parser.add_argument('--Tag', help = "tag", type = str, default = "")
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
#chain = mcmc.Chain(path = Path('/Users/jingyuzhang/Desktop/JetScapeSTAT/bayesian-inference/output/20230829-QM/analysis_jet_substructure_n_walkers_100_long_prod_exponential/mcmc.h5'))
#print(type(chain))
MCMCSamples = chain.load()[::20,:]
#MCMCSamples=pickle.load(f'result/{tag}/mcmc_chain.hdf')['chain']

DoAlt = False
if args.Alternate != '':
    chain2 = mcmc.Chain(path = Path(f'result/{args.Alternate}/mcmc_chain.hdf'))
    MCMCSamples2 = chain2.load()
    DoAlt = True


AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)



import yaml
if args.Config != "":
    with open(args.Config, "r") as stream:
        try:
            Setup = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit()
else:
    Setup = {}

fontsize = 10 if 'FontSize' not in Setup else Setup['FontSize']
labelsize = fontsize if 'LabelSize' not in Setup else Setup['LabelSize']

NDimension = len(AllData["labels"])
Ranges = np.array(AllData["ranges"]).T
# figure, axes = plt.subplots(figsize = (3 * NDimension, 3 * NDimension), ncols = NDimension, nrows = NDimension)

NFigure = NDimension
PanelList = range(0, NDimension)

if 'Reorder' in Setup:
    NFigure = len(Setup['Reorder'])
    PanelList = Setup['Reorder']

if 'Transform' in Setup:
    for i, action in enumerate(Setup['Transform']):
        if action == 'exp':
            MCMCSamples[:,i] = np.exp(MCMCSamples[:,i])
            Ranges[:,i] = np.exp(Ranges[:,i])
        if action == 'log':
            MCMCSamples[:,i] = np.log(MCMCSamples[:,i])
            Ranges[:,i] = np.log(Ranges[:,i])

if 'RangeOverride' in Setup:
    for i, range in enumerate(Setup['RangeOverride']):
        if range[0] != 'None':
            Ranges[0,i] = range[0]
        if range[1] != 'None':
            Ranges[1,i] = range[1]

figure = plt.figure(figsize = (1.6 * (NFigure), 1.5 * (NFigure)))
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
            color = "red" if DoAlt else "green"
            label = args.NominalLabel if i == 0 else ''
            labelAlt = args.AlternateLabel if i == 0 else ''
            ax.hist(MCMCSamples[:,PanelList[i]], bins=50,
                    range=Ranges[:,PanelList[i]], histtype='step', color=color, label = label)
            if DoAlt:
                ax.hist(MCMCSamples2[:,PanelList[i]], bins=50,
                        range=Ranges[:,PanelList[i]], histtype='step', color='blue', label = labelAlt)
            ax.axvline(x = Truth[PanelList[i]], ymin = 0, color='red', linestyle='dotted', linewidth=5)
            if i == 0:
                custom_lines = [
                    Line2D([0], [0], color='red', linestyle='-', linewidth=2, label=label),
                    Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label=labelAlt)
                ]
                ax.legend(handles=custom_lines, loc="upper left", frameon=False, handlelength=1, fontsize='small')
            ax.set_xlabel(Names[PanelList[j]], fontsize = fontsize)
            ax.set_ylabel(Names[PanelList[i]], fontsize = fontsize)
            ax.set_xlim(*Ranges[:,PanelList[j]])
            ax.tick_params(axis = 'x', labelsize = labelsize)
            ax.label_outer()
            if 'Ticks' in Setup:
                ax.get_xaxis().set_ticks(Setup['Ticks'][PanelList[j]])
            ax.label_outer()
            ax_right = ax.secondary_yaxis('right')
            ax_top = ax.secondary_xaxis('top')

            ax.get_yaxis().set_ticks([])
            ax_right.get_yaxis().set_ticks([])
            ax_top.get_xaxis().set_ticks([])
            if i == len(axes)-1:
                ax_right.set_ylabel(Names[PanelList[j]], fontsize = fontsize)
            if i == 0:
                ax_top.set_xlabel(Names[PanelList[i]], fontsize = fontsize)

                
        if i>j:
            color = "Reds" if DoAlt else "Greens"
            ax.hist2d(MCMCSamples[:, PanelList[j]], MCMCSamples[:, PanelList[i]],
                      bins=50, range=[Ranges[:,PanelList[j]], Ranges[:,PanelList[i]]],
                      cmap=color)
            ax.scatter(Truth[PanelList[j]], Truth[PanelList[i]], s = 80, linewidths = 2.5, marker = 'o', facecolors = 'none', edgecolors = 'r')
            ax.set_xlabel(Names[PanelList[j]], fontsize = fontsize)
            ax.set_ylabel(Names[PanelList[i]], fontsize = fontsize)
            ax.tick_params(axis = 'x', labelsize = labelsize)
            ax.tick_params(axis = 'y', labelsize = labelsize)
            ax.set_xlim(*Ranges[:,PanelList[j]])
            ax.set_ylim(*Ranges[:,PanelList[i]])
            if 'Ticks' in Setup:
                ax.get_xaxis().set_ticks(Setup['Ticks'][PanelList[j]])
                ax.get_yaxis().set_ticks(Setup['Ticks'][PanelList[i]])
            ax.label_outer()
            
        if i<j:
            if not DoAlt:
                ax.axis('off')
            else:
                ax.hist2d(MCMCSamples2[:, PanelList[j]], MCMCSamples2[:, PanelList[i]],
                    bins=50, range=[Ranges[:,PanelList[j]], Ranges[:,PanelList[i]]],
                    cmap='Blues')
                ax.scatter(Truth[PanelList[j]], Truth[PanelList[i]], s = 80, linewidths = 2.5, marker = 'o', facecolors = 'none', edgecolors = 'r')
                ax.set_xlabel(Names[PanelList[j]], fontsize = fontsize)
                ax.set_ylabel(Names[PanelList[i]], fontsize = fontsize)
                if i == 0:
                    ax_top = ax.secondary_xaxis('top')
                    ax_top.set_xlabel(Names[PanelList[j]], fontsize = fontsize)
                if j == len(axes)-1:
                    ax_right = ax.secondary_yaxis('right')
                    ax_right.set_ylabel(Names[PanelList[i]], fontsize = fontsize)
                    ax_right.label_outer()

                #ax.spines['right'].set_visible(True)
                ax.tick_params(axis = 'x', labelsize = labelsize, labeltop=True, top=True)
                ax.tick_params(axis = 'y', labelsize = labelsize, labelright=True, right=True)
                ax.set_xlim(*Ranges[:,PanelList[j]])
                ax.set_ylim(*Ranges[:,PanelList[i]])
                if 'Ticks' in Setup:
                    ax.get_xaxis().set_ticks(Setup['Ticks'][PanelList[j]])
                    ax.get_yaxis().set_ticks(Setup['Ticks'][PanelList[i]])
                ax.label_outer()
                

Suffix = ''
if 'Suffix' in Setup:
    Suffix = '_' + Setup['Suffix']

plt.tight_layout()
tag = AllData['tag']
#print(tag)
plt.savefig(f'result/{tag}/plots/Correlation{Suffix}.pdf', dpi = 192)
plt.savefig(f'result/{tag}/plots/Correlation{Suffix}.png', dpi = 192)
# plt.savefig(f'result/{tag}/plots/Correlation.png', dpi = 192)


