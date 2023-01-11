import matplotlib.pyplot as plt
import numpy as np
import yaml

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

TempPrediction = AllData["model"]

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--Config", help = "plot configuration file", type = str, default = "yaml/PlotConfig.yaml")
args = parser.parse_args()

def MakePlot(ToPlot, Suffix, Label, Common, Correlation):
    # Let's not remove things silently.  We should let fails fail for this
    # ToPlot = [x for x in ToPlot if x in AllData["observables"][0][1]]

    if Suffix != "":
        Suffix = "_" + Suffix

    if Correlation == True:
        TypeString = "Correlation"
    else:
        TypeString = "Covariance"

    if len(ToPlot) == 0:
        print("Nothing valid specified")
        return

    SystemCount = len(AllData["systems"])
    BinCount = len(ToPlot)

    figure = plt.figure(figsize = (3 * BinCount + 1, 3 + 1))
    gridspec = figure.add_gridspec(1, BinCount)
    axes = gridspec.subplots()

    if BinCount == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        ax.set_xlabel(r"$p_{T}$ index", fontsize = 15)
        ax.set_ylabel("")

        if i < len(Label):
            ax.text(0.95, 0.95, Label[i],
                verticalalignment='top', horizontalalignment='right',
                transform = ax.transAxes, fontsize = 15, color='white')

        if ToPlot[i] not in AllData["observables"][0][1]:
            continue

        Cov = AllData["cov"]["HeavyIon"][("R_AA", ToPlot[i])][("R_AA", ToPlot[i])]
        if Cov.any() != None:
            if Correlation == True:
                Diag = np.sqrt(np.diag(Cov))
                Cov = Cov / Diag[:,None] / Diag[None,:]
            ax.imshow(Cov, vmin = 0)

        # ax.label_outer()

    axes[0].set_title(Common, loc = 'left', fontsize = 15)
    axes[0].set_ylabel(r"$p_{T}$ index", fontsize = 15)

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/SmallDiagonal{TypeString}{Suffix}.pdf', dpi = 192)
    plt.close('all')


with open(args.Config, 'r') as stream:
    try:
        setup = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

for item in setup['ObservablePlot']:
    MakePlot(item['Key'], item['Suffix'], item['Label'], item['Common'], True)
    MakePlot(item['Key'], item['Suffix'], item['Label'], item['Common'], False)


