import os.path
from os import path
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--Tag", help = "result folder name", default = "STAT20221012ExponentialMatern_N6")
args = parser.parse_args()

print('Recalling analysis from results folder result/{}/'.format(args.Tag))

if path.isdir('result/{}/'.format(args.Tag)) == False:
    print('Result folder not found')
    exit()

if path.isfile('result/{}/default.p'.format(args.Tag)) == False:
    print('Settings file not found')
    exit()

shutil.copyfile('result/{}/default.p'.format(args.Tag),      'input/default.p', )

if path.isfile('result/{}/HeavyIon.pkl'.format(args.Tag)) == False:
    print('Cache file not found')
    exit()

shutil.copyfile('result/{}/HeavyIon.pkl'.format(args.Tag),   'cache/emulator/HeavyIon.pkl')

if path.isfile('result/{}/mcmc_chain.hdf'.format(args.Tag)) == True:
    shutil.copyfile('result/{}/mcmc_chain.hdf'.format(args.Tag), 'cache/mcmc_chain.hdf')
    print('Copied settings file, cache file and MCMC chain')
else:
    print('Copied settings file and cache file.  MCMC chain not found so skipped.')





