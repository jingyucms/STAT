import matplotlib.pyplot as plt
import numpy as np

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

from src import lazydict, emulator
Emulator = emulator.Emulator.from_cache('HeavyIon')

Y = []
for (obs, subobslist) in AllData['observables']:
    for subobs in subobslist:
        Y.append(AllData['model']['HeavyIon'][obs][subobs]['Y'])
Y = np.concatenate(Y, axis=1)

Z = Emulator.pca.transform(Emulator.scaler.transform(Y))

NDim = min(int(AllData['design'].shape[0] / 2), Z.shape[1])
NPar = AllData['design'].shape[1]

LinearCorrelation = np.zeros((NPar, NDim))

for i in range(0, NDim):
    figure = plt.figure(figsize = (3 * NPar + 1, 3 + 1))
    gridspec = figure.add_gridspec(1, NPar, hspace = 0, wspace = 0)
    axes = gridspec.subplots(sharex = 'col', sharey = 'row')

    for j, ax in enumerate(axes):
        ax.set_xlabel(AllData["labels"][j])
        ax.set_ylabel(f'PCA ({i})')

        ax.plot(AllData['design'][:,j], Z[:,i], 'go')
        ax.label_outer()

        LinearCorrelation[j,i] = np.abs(np.corrcoef(AllData['design'][:,j], Z[:,i])[0,1])

    axes[0].set_title(f'PCA axis {i} correlations', loc = 'left', fontsize = 15)

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/PCACorrelationAxis{i}.pdf', dpi = 192)
    plt.close('all')

figure, axis = plt.subplots(figsize = (6, 4))
pos = axis.imshow(LinearCorrelation, vmin = 0, vmax = 1, aspect = 'auto')
axis.set_xlabel('PCA Index')
axis.set_yticks(np.arange(NPar))
axis.set_yticklabels(AllData['labels'])
figure.colorbar(pos, ax = axis, label = '|r|')
figure.savefig(f'result/{tag}/plots/PCACorrelation.pdf', dpi = 192)
plt.close('all')

NZoom = 9
figure, axis = plt.subplots(figsize = (4, 4))
pos = axis.imshow(LinearCorrelation[:,:NZoom], vmin = 0, vmax = 1, aspect = 'auto')
axis.set_xlabel('PCA Index')
axis.set_yticks(np.arange(NPar))
axis.set_yticklabels(AllData['labels'])
for i in range(NZoom):
    for j in range(NPar):
        text = axis.text(i, j, "{:.2f}".format(LinearCorrelation[j,i]), ha="center", va="center", color="w", rotation=90)
figure.colorbar(pos, ax = axis, label = '|r|')
figure.savefig(f'result/{tag}/plots/PCACorrelationZoomIn.pdf', dpi = 192)
plt.close('all')




