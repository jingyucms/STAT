import os
import pickle
import numpy as np
import subprocess
from src import mcmc
import matplotlib.pyplot as plt

chain = mcmc.Chain()

AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)
tag = AllData['tag']

AllSample = {}
with open(f'result/{tag}/CScan.p', 'rb') as handle:
    AllSample = pickle.load(handle)

C = np.array(list(AllSample.keys()))
Max = np.zeros(C.shape)
Average = np.zeros(C.shape)

print(C)

for i, c in enumerate(C):

    chain.set_mcmc_variables(data_c_factor = c)
    Posterior = np.concatenate(list(map(chain.log_posterior, AllSample[c])))

    print(c)
    print(Posterior[:10])

    Max[i] = np.max(Posterior)
    Average[i] = np.log(np.average(np.exp(Posterior - Max[i]))) + Max[i]

# print(C)
# print(Max)
# print(Average)

PanelCount = 1
figure = plt.figure(figsize = (3 + 1, 3 * PanelCount + 1))
gridspec = figure.add_gridspec(PanelCount, 1, hspace = 0, wspace = 0)
axes = gridspec.subplots(sharex = 'col', sharey = 'row')

axes.set_xlabel(r'c', fontsize = 15)
axes.set_ylabel(r'log(posterior)', fontsize = 15)
axes.plot(C, Average, 'b-', label = 'Average')
axes.plot(C, Max, 'g-', label = 'Maximum')
axes.legend(loc = 'upper right')
axes.label_outer()

plt.tight_layout()
figure.savefig(f'result/{tag}/plots/CScan.pdf', dpi = 192)
plt.close('all')


