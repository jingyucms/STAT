import matplotlib.pyplot as plt
import numpy as np

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
with open('result/{}/default.p'.format(tag), 'rb') as handle:
    AllData = pickle.load(handle)

from src import lazydict, emulator
#Emulator = emulator.Emulator.from_cache('HeavyIon')
Emulator = emulator.Emulator.from_cache_custom(system='HeavyIon',path=f'result/{tag}/HeavyIon.pkl')

Examples = AllData["design"]

TempPrediction = {"HeavyIon": Emulator.predict(Examples)}

PrePrediction = AllData["model"]

SystemCount = len(AllData["systems"])
BinCount = len(AllData['observables'][0][1])

CC = 4
RC = int(np.ceil(BinCount / CC))

figure, axes = plt.subplots(figsize = (3 * CC, 3 * RC), nrows = RC, ncols = CC)

shape = (BinCount, 185)
dist = np.zeros(shape)

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
    axes[ax][ay].set_title(title)

    print(S2, TempPrediction[S1][O][S2].shape, PrePrediction[S1][O][S2]['Y'].shape)
    for i, y in enumerate(TempPrediction[S1][O][S2]):
        if "CMS" in S2:
            dist[s2][i] = np.sum(abs(PrePrediction[S1][O][S2]['Y'][i][:]-y[:]))
        else:
            dist[s2][i] = np.sum(abs(PrePrediction[S1][O][S2]['Y'][i][:]-y[:]))
        #if "CMS" in S2:
        #    dist[s2][i] = np.std(PrePrediction[S1][O][S2]['Y'][:,:4])
            #print(S2, PrePrediction[S1][O][S2]['Y'][:,-5:])
        #else:
        #    dist[s2][i] = np.std(PrePrediction[S1][O][S2]['Y'][:,-4:])
            #print(S2, PrePrediction[S1][O][S2]['Y'][:,:5])

    for i, y in enumerate(TempPrediction[S1][O][S2]):
        axes[ax][ay].plot(DX, y, 'b-', alpha=0.2, label="Posterior" if i==0 else '')
    axes[ax][ay].errorbar(DX, DY, yerr = DE, fmt='ro', label="Measurements")
    axes[ax][ay].set_xscale('log')

print(dist.shape)    
dist = np.sum(dist, axis=0)
print(dist.shape)
    
top_10_indices = np.argsort(dist)[-20:][::-1]
print(', '.join(map(str, top_10_indices)))

plt.tight_layout()
tag = AllData['tag']
figure.savefig(f'result/{tag}/plots/ObservableDesign.pdf', dpi = 192)
# figure.savefig(f'result/{tag}/plots/ObservableDesign.png', dpi = 192)


