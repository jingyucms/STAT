
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle

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

NDimension = len(AllData["labels"])
Ranges = np.array(AllData["ranges"]).T
DesignPoints = AllData["design"]
#print(len(DesignPoints), DesignPoints)
#DesignPoints = DesignPoints[[68, 62, 131, 48, 67, 92, 26, 87, 105, 47, 36, 57, 157, 21, 49, 46, 79, 97, 122, 75]]
#DesignPoints = DesignPoints[[141, 58, 49, 1, 47, 42, 84, 61, 39, 117, 144, 52, 150, 40, 146, 128, 107, 100, 51, 115]]
DesignPoints = DesignPoints[[28, 92, 46, 104, 154, 22, 48, 103, 107, 115]]

# figure, axes = plt.subplots(figsize = (3 * NDimension, 3 * NDimension), ncols = NDimension, nrows = NDimension, sharex='col', sharey='row')
figure = plt.figure(figsize = (1.5 * (NDimension), 1.5 * (NDimension)))
gridspec = figure.add_gridspec(NDimension, NDimension, hspace = 0, wspace = 0)
axes = gridspec.subplots(sharex = 'col', sharey = 'row')
Names = AllData["labels"]
for i, row in enumerate(axes):
    for j, ax in enumerate(row):
        if i + 1 > j:
            # ax.hist2d(DesignPoints[:, j], DesignPoints[:, i],
            #           bins=50, range=[Ranges[:,j], Ranges[:,i]],
            #           cmap='Greens')
            ax.plot(DesignPoints[:,j], DesignPoints[:,i], 'bo')
            ax.set_xlabel(Names[j])
            ax.set_ylabel(Names[i])
            ax.set_xlim(*Ranges[:,j])
            ax.set_ylim(*Ranges[:,i])
            ax.label_outer()
        if i + 1 <= j:
            ax.axis('off')
plt.tight_layout()
tag = AllData['tag']
plt.savefig(f'result/{tag}/plots/DesignPoints.pdf', dpi = 192)
# plt.savefig(f'result/{tag}/plots/DesignPoints.png', dpi = 192)
# figure
