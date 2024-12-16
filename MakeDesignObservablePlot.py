import matplotlib.pyplot as plt
import numpy as np
import statistics

import pickle
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--Tag', help = 'tag for the nominal', type = str, default = '')
args = parser.parse_args()

AllDataTag = {}
with open('input/default_tag.p', 'rb') as handle:
    AllDataTag = pickle.load(handle)

tag = AllDataTag["tag"]
if args.Tag != "": tag = args.Tag

AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

TempPrediction = AllData["model"]

SystemCount = len(AllData["systems"])
BinCount = len(AllData['observables'][0][1])

CC = 5
RC = int(np.ceil(BinCount / CC))

figure, axes = plt.subplots(figsize = (3 * CC, 3 * RC), nrows = RC, ncols = CC)


counter = 0
for s2 in range(0, RC * CC):
    ax = int(np.floor(s2 / CC))
    ay = s2 % CC
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

    #print(DY)
    counter += len(DY)

    t = AllData["observables"][0][1][s2].replace('Inclusive','').split('_')
    title = '{}_{}\n{}_{}_{}'.format(t[0],t[1],t[2],t[3],t[4])
    axes[ax][ay].set_title(title)

    #print(S2, TempPrediction[S1][O][S2]['Y'].shape)

    for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][:]):
    #for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][[68, 62, 131, 48, 67, 92, 26, 87, 105, 47, 36, 57, 157, 21, 49, 46, 79, 97, 122, 75]]):
    #for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][[141, 58, 49, 1, 47, 42, 84, 61, 39, 117, 144, 52, 150, 40, 146, 128, 107, 100, 51, 115]]):
    #for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][[92, 57, 66, 65, 64, 63, 62, 61, 60, 59]]):
    #for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][[28, 92, 46, 104, 154, 22, 48, 103, 107, 115]]):
    ## This is ugly, but leave for now
    # For JetSubOnly_Centrality10_V10 config
    #for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][[46, 115, 75, 92, 22, 104, 28, 120, 154, 93]]):
    # For JetSubOnly_allCentrality config
    #for i, y in enumerate(TempPrediction[S1][O][S2]['Y'][[63, 152, 100, 123, 25, 139, 34, 158, 196, 124]]):
        axes[ax][ay].plot(DX, y, 'b-', alpha=0.2, label="Posterior" if i==0 else '')
    axes[ax][ay].errorbar(DX, DY, yerr = DE, fmt='ro', label="Measurements")
    axes[ax][ay].set_xscale('log')
    
#print(counter)
plt.tight_layout()
tag = AllData['tag']
figure.savefig(f'result/{tag}/plots/Design.pdf', dpi = 192)
# figure.savefig(f'result/{tag}/plots/Design.png', dpi = 192)
