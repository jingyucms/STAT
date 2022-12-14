
import matplotlib.pyplot as plt
import numpy as np

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

NDimension = len(AllData["labels"])
Ranges = np.array(AllData["ranges"]).T
DesignPoints = AllData["design"]

# figure, axes = plt.subplots(figsize = (3 * NDimension, 3 * NDimension), ncols = NDimension, nrows = NDimension, sharex='col', sharey='row')
figure = plt.figure(figsize = (1.5 * (NDimension - 1), 1.5 * (NDimension - 1)))
gridspec = figure.add_gridspec(NDimension - 1, NDimension - 1, hspace = 0, wspace = 0)
axes = gridspec.subplots(sharex = 'col', sharey = 'row')
Names = AllData["labels"]
for i, row in enumerate(axes):
    for j, ax in enumerate(row):
        if i + 1 > j:
            # ax.hist2d(DesignPoints[:, j], DesignPoints[:, i],
            #           bins=50, range=[Ranges[:,j], Ranges[:,i]],
            #           cmap='Greens')
            ax.plot(DesignPoints[:,j], DesignPoints[:,i+1], 'bo')
            ax.set_xlabel(Names[j])
            ax.set_ylabel(Names[i+1])
            ax.set_xlim(*Ranges[:,j])
            ax.set_ylim(*Ranges[:,i+1])
            ax.label_outer()
        if i + 1 <= j:
            ax.axis('off')
plt.tight_layout()
tag = AllData['tag']
plt.savefig(f'result/{tag}/plots/DesignPoints.pdf', dpi = 192)
# plt.savefig(f'result/{tag}/plots/DesignPoints.png', dpi = 192)
# figure
