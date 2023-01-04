import matplotlib.pyplot as plt
import numpy as np

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

import src
src.Initialize()
from src import mcmc
chain = mcmc.Chain()
MCMCSamples = chain.load()

from src import lazydict, emulator
Emulator = emulator.Emulator.from_cache('HeavyIon')

Examples = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 500), :]

TempPrediction = {"HeavyIon": Emulator.predict(Examples)}

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--ToPlot", help = "which ones to plot", type = str, nargs = "+")
# parser.add_argument("--Suffix", help = "suffix to add to the file name", type = str, default = "")
# args = parser.parse_args()

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
        # S2 = AllData["observables"][0][1][s2]

        DX = AllData["data"][S1][O][S2]['x']
        DY = AllData["data"][S1][O][S2]['y']
        DE = np.sqrt(AllData["data"][S1][O][S2]['yerr']['stat'][:,0]**2 + AllData["data"][S1][O][S2]['yerr']['sys'][:,0]**2)

        # ax.set_title(S2)
        # ax.set_xscale('log')

        for j, y in enumerate(TempPrediction[S1][O][S2]):
            if len(DX) > 1:
                ax.plot(DX, y, 'b-', alpha=0.05)
            else:
                ax.plot([np.floor(DX[0] * 0.9), np.ceil(DX[0] * 1.1)], [y[0], y[0]], 'b-', alpha=0.05)
        ax.errorbar(DX, DY, yerr = DE, fmt='ro', label="Measurements")

        if i < len(Label):
            ax.text(0.05, 0.95, Label[i],
                verticalalignment='top', horizontalalignment='left',
                transform = ax.transAxes, fontsize = 15)

        ax.set_ylim([0, 1.2])
        ax.label_outer()

    axes[0].set_title(Common, loc = 'left', fontsize = 15)

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/SmallObservablePosterior{Suffix}.pdf', dpi = 192)
    plt.close('all')

MakePlot(['ALICE_2760_Hadron_ch_0_5', 'ALICE_2760_Hadron_ch_5_10', 'ALICE_2760_Hadron_ch_10_20', 'ALICE_2760_Hadron_ch_20_30', 'ALICE_2760_Hadron_ch_30_40', 'ALICE_2760_Hadron_ch_40_50'], 'ALICE_Hadron2760', ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%'], 'ALICE, 2.76 TeV, Charged Hadron')
MakePlot(['ALICE_2760_Hadron_pi0_0_10', 'ALICE_2760_Hadron_pi0_20_50'], 'ALICE_Pi02760', ['0-10%', '20-50%'], r'ALICE, 2.76 TeV, $\pi^0$')
MakePlot(['ALICE_2760_Hadron_pi_0_5', 'ALICE_2760_Hadron_pi_5_10', 'ALICE_2760_Hadron_pi_10_20', 'ALICE_2760_Hadron_pi_20_40'], 'ALICE_Pi2760', ['0-5%', '5-10%', '10-20%', '20-40%'], r'ALICE, 2.76 TeV, $\pi$')
MakePlot(['ALICE_2760_Jet_R02_0_10', 'ALICE_2760_Jet_R02_10_30'], 'ALICE_Jet2760', ['0-10%', '10-30%'], 'ALICE, 2.76 TeV, Jet R = 0.2')
MakePlot(['ALICE_5020_Hadron_ch_0_5', 'ALICE_5020_Hadron_ch_5_10', 'ALICE_5020_Hadron_ch_10_20', 'ALICE_5020_Hadron_ch_20_30', 'ALICE_5020_Hadron_ch_30_40', 'ALICE_5020_Hadron_ch_40_50'], 'ALICE_Hadron5020', ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%'], 'ALICE, 5.02 TeV, Charged Hadron')
MakePlot(['ALICE_5020_Hadron_pi_0_5', 'ALICE_5020_Hadron_pi_5_10', 'ALICE_5020_Hadron_pi_10_20', 'ALICE_5020_Hadron_pi_20_30', 'ALICE_5020_Hadron_pi_30_40', 'ALICE_5020_Hadron_pi_40_50'], 'ALICE_Pi5020', ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%'], r'ALICE, 5.02 TeV, $\pi$')
MakePlot(['ALICE_5020_Jet_R02_0_10', 'ALICE_5020_Jet_R04_0_10'], 'ALICE_Jet5020', ['R = 0.2', 'R = 0.4'], 'ALICE, 5.02 TeV, Jet, 0-10%')
MakePlot(['ATLAS_2760_Hadron_ch_0_5', 'ATLAS_2760_Hadron_ch_5_10', 'ATLAS_2760_Hadron_ch_10_20', 'ATLAS_2760_Hadron_ch_20_30', 'ATLAS_2760_Hadron_ch_30_40', 'ATLAS_2760_Hadron_ch_40_50'], 'ATLAS_Hadron2760', ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%'], 'ATLAS, 2.76 TeV, Charged Hadron')
MakePlot(['ATLAS_2760_Jet_R04_0_10', 'ATLAS_2760_Jet_R04_10_20', 'ATLAS_2760_Jet_R04_20_30', 'ATLAS_2760_Jet_R04_30_40', 'ATLAS_2760_Jet_R04_40_50'], 'ATLAS_Jet2760', ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%'], 'ATLAS, 2.76 TeV, Jet R = 0.4')
MakePlot(['ATLAS_5020_Jet_R04_0_10', 'ATLAS_5020_Jet_R04_10_20', 'ATLAS_5020_Jet_R04_20_30', 'ATLAS_5020_Jet_R04_30_40', 'ATLAS_5020_Jet_R04_40_50'], 'ATLAS_Jet5020', ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%'], 'ATLAS, 5.02 TeV, Jet R = 0.4')
MakePlot(['CMS_2760_Hadron_ch_0_5', 'CMS_2760_Hadron_ch_5_10', 'CMS_2760_Hadron_ch_10_30'], 'CMS_Hadron2760', ['0-5%', '5-10%', '10-30%'], 'CMS, 2.76 TeV, Charged Hadron')
MakePlot(['CMS_2760_Jet_R02_0_5', 'CMS_2760_Jet_R02_5_10', 'CMS_2760_Jet_R02_10_30', 'CMS_2760_Jet_R02_30_50'], 'CMS_Jet2760R02', ['0-5%', '5-10%', '10-30%', '30-50%'], 'CMS, 2.76 TeV, Jet R = 0.2')
MakePlot(['CMS_2760_Jet_R03_0_5', 'CMS_2760_Jet_R03_5_10', 'CMS_2760_Jet_R03_10_30', 'CMS_2760_Jet_R03_30_50'], 'CMS_Jet2760R03', ['0-5%', '5-10%', '10-30%', '30-50%'], 'CMS, 2.76 TeV, Jet R = 0.3')
MakePlot(['CMS_2760_Jet_R04_0_5', 'CMS_2760_Jet_R04_5_10', 'CMS_2760_Jet_R04_10_30', 'CMS_2760_Jet_R04_30_50'], 'CMS_Jet2760R04', ['0-5%', '5-10%', '10-30%', '30-50%'], 'CMS, 2.76 TeV, Jet R = 0.4')
MakePlot(['CMS_5020_Hadron_ch_0_5', 'CMS_5020_Hadron_ch_5_10', 'CMS_5020_Hadron_ch_10_30', 'CMS_5020_Hadron_ch_30_50'], 'CMS_Hadron5020', ['0-5%', '5-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Charged Hadron')
MakePlot(['CMS_5020_Jet_R02_0_10', 'CMS_5020_Jet_R02_10_30', 'CMS_5020_Jet_R02_30_50'], 'CMS_Jet5020R02', ['0-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Jet R = 0.2')
MakePlot(['CMS_5020_Jet_R03_0_10', 'CMS_5020_Jet_R03_10_30', 'CMS_5020_Jet_R03_30_50'], 'CMS_Jet5020R03', ['0-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Jet R = 0.3')
MakePlot(['CMS_5020_Jet_R04_0_10', 'CMS_5020_Jet_R04_10_30', 'CMS_5020_Jet_R04_30_50'], 'CMS_Jet5020R04', ['0-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Jet R = 0.4')
MakePlot(['CMS_5020_Jet_R06_0_10', 'CMS_5020_Jet_R06_10_30', 'CMS_5020_Jet_R06_30_50'], 'CMS_Jet5020R06', ['0-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Jet R = 0.6')
MakePlot(['CMS_5020_Jet_R08_0_10', 'CMS_5020_Jet_R08_10_30', 'CMS_5020_Jet_R08_30_50'], 'CMS_Jet5020R08', ['0-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Jet R = 0.8')
MakePlot(['CMS_5020_Jet_R10_0_10', 'CMS_5020_Jet_R10_10_30', 'CMS_5020_Jet_R10_30_50'], 'CMS_Jet5020R10', ['0-10%', '10-30%', '30-50%'], 'CMS, 5.02 TeV, Jet R = 1.0')
MakePlot(['PHENIX_200_Hadron_pi0_0_10', 'PHENIX_200_Hadron_pi0_10_20', 'PHENIX_200_Hadron_pi0_20_30', 'PHENIX_200_Hadron_pi0_30_40', 'PHENIX_200_Hadron_pi0_40_50'], 'PHENIX_Pi0200', ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%'], 'PHENIX, 200 GeV, pi0')
MakePlot(['STAR_200_Hadron_ch_0_5', 'STAR_200_Hadron_ch_10_20', 'STAR_200_Hadron_ch_20_30', 'STAR_200_Hadron_ch_30_40'], 'STAR_Hadron200', ['0-5%', '10-20%', '20-30%', '30-40%'], 'STAR, 200 GeV, Charged Hadron')
MakePlot(['STAR_200_ChargedJet_R02_0_10', 'STAR_200_ChargedJet_R04_0_10'], 'STAR_ChargedJet200', ['R = 0.2', 'R = 0.4'], 'STAR, 200 GeV, Charged Jet, 0-10%')






