
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--CFactor", help = "c factor to use", default = 0.00, type = float)
parser.add_argument("--Tag", help = "tag", type = str, default = "")
args = parser.parse_args()

import pickle
AllDataTag = {}
with open('input/default_tag.p', 'rb') as handle:
    AllDataTag = pickle.load(handle)
tag = AllDataTag["tag"]
if args.Tag != "": tag = args.Tag 

AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

print(AllData['mcmc'])

import subprocess
subprocess.call(['python3', '-m', 'src.mcmc',
                 '--nwalkers', str(AllData['mcmc']['walker']),
                 '--nburnsteps', str(AllData['mcmc']['burn']),
                 str(AllData['mcmc']['step']),
                 '--data_c_factor', str(args.CFactor)])

import shutil
shutil.copyfile('cache/mcmc_chain.h5', 'result/{}/mcmc_chain.h5'.format(AllData['tag']))
import os
os.remove('cache/mcmc_chain.h5')
