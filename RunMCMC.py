
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--CFactor", help = "c factor to use", default = 0.00, type = float)
args = parser.parse_args()


import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

print(AllData['mcmc'])

import subprocess
subprocess.call(['python3', '-m', 'src.mcmc',
                 '--nwalkers', str(AllData['mcmc']['walker']),
                 '--nburnsteps', str(AllData['mcmc']['burn']), str(AllData['mcmc']['step']),
                 '--data_c_factor', str(args.CFactor)])

import shutil
shutil.copyfile('cache/mcmc_chain.hdf', 'result/{}/mcmc_chain.hdf'.format(AllData['tag']))
