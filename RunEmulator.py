import pickle,sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--Tag", help = "tag", type = str, default = "")
args = parser.parse_args()


AllDataTag = {}
with open('input/default_tag.p', 'rb') as handle:
    AllDataTag = pickle.load(handle)
tag = AllDataTag["tag"]
if args.Tag != "": tag = args.Tag 

AllData = {}
with open(f'result/{tag}/default.p', 'rb') as handle:
    AllData = pickle.load(handle)
    
import subprocess
subprocess.call(['python3', '-m', 'src.emulator',
                 '--retrain', '--npc', str(AllData['emulator']['npc']),
                 '--kernelchoice', AllData['emulator']['kernel'],
                 '--nu', str(AllData['emulator']['nu'] if 'nu' in AllData['emulator'] else 1.5),
                 '--nrestarts', str(AllData['emulator']['retrain']),
                 '--alpha', '0.1'])

import shutil
shutil.copyfile('cache/emulator/HeavyIon.pkl', 'result/{}/HeavyIon.pkl'.format(AllData['tag']))
