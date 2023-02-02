import os
import pickle
import numpy as np
import subprocess
from src import mcmc
import matplotlib.pyplot as plt

AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

AllSample = {}

C = np.linspace(-0.1, 0.1, 21)
Max = np.zeros(C.shape)
Average = np.zeros(C.shape)

for i, c in enumerate(C):

    print(f'Doing scan with c = {c} now')

    if os.path.exists('cache/mcmc_chain.hdf'):
        os.remove('cache/mcmc_chain.hdf')

    BurnStep = 1000
    ProductionStep = 250

    subprocess.call(['python3', '-m', 'src.mcmc',
                 '--nwalkers', str(AllData['mcmc']['walker']),
                 '--nburnsteps', str(BurnStep), str(ProductionStep),
                 '--data_c_factor', str(c)])
    # subprocess.call(['python3', '-m', 'src.mcmc',
    #              '--nwalkers', str(AllData['mcmc']['walker']),
    #              '--nburnsteps', str(AllData['mcmc']['burn']), str(AllData['mcmc']['step']),
    #              '--data_c_factor', str(c)])

    SampleSize = AllData['mcmc']['walker'] * ProductionStep
    if SampleSize > 1000:
        Thinning = int(np.floor(SampleSize / 1000))
    else:
        Thinning = 1

    chain = mcmc.Chain()
    MCMCSamples = chain.load()

    AllSample[c] = MCMCSamples

    print(MCMCSamples.shape)

    chain.set_mcmc_variables(data_c_factor = c)
    Posterior = chain.log_posterior(MCMCSamples[::Thinning,:])

    # print(Posterior)

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

# axes[1].set_xlabel(r'c', fontsize = 15)
# axes[1].set_ylabel(r'Max posterior', fontsize = 15)
# axes[1].plot(C, Max, 'g-')
# axes[1].label_outer()

plt.tight_layout()
tag = AllData['tag']
figure.savefig(f'result/{tag}/plots/CScan.pdf', dpi = 192)
plt.close('all')

with open(f'result/{tag}/CScan.p', 'wb') as handle:
    pickle.dump(AllSample, handle, protocol = pickle.HIGHEST_PROTOCOL)


