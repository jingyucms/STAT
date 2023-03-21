import numpy as np
import src.reader as Reader
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--Config', help = "config file", default = "yaml/DataProcessing20230320.yaml")
# parser.add_argument("--Input", help = "input file",
#     default = 'input/STAT20230320Exponential/Data_ALICE_PbPb2760_hadron_RAA_ch_0-5_2018.dat')
# parser.add_argument('--Output', help = "output file", default = "test.dat")
# parser.add_argument("--Percentage", help = "extra uncertainty percentage", nargs = '+', type = float, default = [])
# parser.add_argument("--Label", help = "labels of extra uncertainties", nargs = '+', type = str, default = [])
args = parser.parse_args()


with open(args.Config, "r") as stream:
    try:
        Setup = yaml.safe_load(stream)

    except yaml.YAMLError as exc:
        print(exc)
        exit()

def ProcessOneData(Input, Output, Percentage, Label):
    Data = Reader.ReadData(Input)

    for i in list(range(0, len(Percentage))):
        Data['SysLabel'].append(Label[i])
        Data['Label'].append(Label[i])
        Data['Data']['yerr']['sys'] = \
            np.concatenate((Data['Data']['yerr']['sys'], np.array([Data['Data']['y'] * Percentage[i]]).T), axis = 1)

    Reader.WriteData(Output, Data)

for Item in Setup['Data']:
    Input = Setup['InputDirectory'] + '/' + Setup['Data'][Item]['Input']
    Output = Setup['OutputDirectory'] + '/' + Setup['Data'][Item]['Output']
    Percentage = [] if 'Percentage' not in Setup['Data'][Item] else Setup['Data'][Item]['Percentage']
    Label = [] if 'Label' not in Setup['Data'][Item] else Setup['Data'][Item]['Label']
    ProcessOneData(Input, Output, Percentage, Label)





