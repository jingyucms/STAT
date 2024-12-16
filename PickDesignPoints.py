import numpy as np
import pickle
from pathlib import Path
import src.reader as Reader
import yaml
import sys
import argparse
from scipy import stats

# Initialize temporary containers
DataList = []
Setup = {}
RawData = {}
RawPrediction = {}
RawPredictionError = {}
RawDesign = {}

parser = argparse.ArgumentParser()
parser.add_argument("--Config", help = "Config yaml file", default = "yaml/TestAnalysis.yaml")
parser.add_argument("--Holdout", help = "Holdout test", default = -1, type = int)
parser.add_argument("--CentralityMin", help = "Centrality range", default = -1, type = int)
parser.add_argument("--CentralityMax", help = "Centrality range", default = -1, type = int)
parser.add_argument("--EnergyMin", help = "Energy range", default = -1, type = int)
parser.add_argument("--EnergyMax", help = "Energy range", default = -1, type = int)
parser.add_argument("--DoSmoothing", help = "Switch to smooth predictions", action = "store_true")
parser.add_argument("--DefaultSysLength", help = "default correlation length", default = 0.1, type = float)
parser.add_argument("--TagSuffix", help = "Suffix to add to the tag", default = "", type = str)
parser.add_argument("--Observable", help = "which observable to use", default = "", type = str)
parser.add_argument("--Omit", help = "omit specific datasets", nargs = '+', type = str, default = [])
args = parser.parse_args()


print("")
print(f"Setting up new analysis with config {args.Config}")
print("")

###################################################
# Part 1: read raw data and prediction and design #
###################################################

ConfigFile = args.Config

with open(ConfigFile, "r") as stream:
    try:
        Setup = yaml.safe_load(stream)

    except yaml.YAMLError as exc:
        print(exc)
        exit()

Tag = Setup["Tag"]
if args.TagSuffix != '':
    Tag = Tag + "_" + args.TagSuffix

if args.CentralityMin >= 0:
    Setup['Data'] = {k: v for k, v in Setup['Data'].items() if v['Attribute']['CentralityMin'] >= args.CentralityMin}
    Tag = Tag + '_CentralityMin' + str(args.CentralityMin)
if args.CentralityMax >= 0:
    Setup['Data'] = {k: v for k, v in Setup['Data'].items() if v['Attribute']['CentralityMax'] <= args.CentralityMax}
    Tag = Tag + '_CentralityMax' + str(args.CentralityMax)
if args.EnergyMin >= 0:
    Setup['Data'] = {k: v for k, v in Setup['Data'].items() if v['Attribute']['Energy'] >= args.EnergyMin}
    Tag = Tag + '_EnergyMin' + str(args.EnergyMin)
if args.EnergyMax >= 0:
    Setup['Data'] = {k: v for k, v in Setup['Data'].items() if v['Attribute']['Energy'] <= args.EnergyMax}
    Tag = Tag + '_EnergyMax' + str(args.EnergyMax)
if args.Observable != "":
    Setup['Data'] = {k: v for k, v in Setup['Data'].items() if args.Observable in v['Attribute']['Observable']}
    Tag = Tag + '_Observable' + args.Observable

# print(Setup['Data'].keys())

FullDataList = list(Setup['Data'].keys())
DataList = [Item for Item in FullDataList if Item not in args.Omit]
RemovedList = [Item for Item in args.Omit if Item in FullDataList]

if len(RemovedList) > 0:
    Tag = Tag + '_Omit'
    for Item in RemovedList:
        Tag = Tag + '_' + Item

for Item in DataList:
    print(Item)
    RawData[Item] = Reader.ReadData(Setup['BaseDirectory'] + Setup['Data'][Item]['Data'])
    RawData[Item]["Data"]["c"] = False   # Initialize c-factor switch to false
    if 'CFactor' in Setup['Data'][Item] and Setup['Data'][Item]['CFactor'] == True:
        RawData[Item]["Data"]["c"] = True
    RawPrediction[Item] = Reader.ReadPrediction(Setup['BaseDirectory'] + Setup['Data'][Item]['Prediction'])
    if 'PredictionError' in Setup['Data'][Item]:
        RawPredictionError[Item] = Reader.ReadPrediction(Setup['BaseDirectory'] + Setup['Data'][Item]['PredictionError'])
    else:
        RawPredictionError[Item] = Reader.ReadPrediction(Setup['BaseDirectory'] + Setup['Data'][Item]['Prediction'])
        RawPredictionError[Item]['Prediction'][:,:] = -1

RawDesign = Reader.ReadDesign(Setup['BaseDirectory'] + Setup['Design']['File'])
#print(len(RawDesign['Design']))
for I in Setup['Design']['LogScale']:
    RawDesign['Design'][:, I] = np.log(RawDesign['Design'][:, I])
    RawDesign['Parameter'][I] = 'log(' + RawDesign['Parameter'][I] + ')'

    Setup['Design']['Range'][I][0] = np.log(Setup['Design']['Range'][I][0])
    Setup['Design']['Range'][I][1] = np.log(Setup['Design']['Range'][I][1])



#########################################################
# Part 2: sort out missing points and extra data points #
#########################################################

def InsertZeroDesign(Raw, Locations):
    for Location in Locations:
        Raw = np.insert(Raw, Location, np.zeros(Raw.shape[1]), axis = 0)
    return Raw

def DeleteRawData(Raw, Items):
    Raw["Data"]["x"]    = np.delete(Raw["Data"]["x"], Items, axis = 0)
    if 'xerr' in Raw['Data']:
        Raw["Data"]["xerr"] = np.delete(Raw["Data"]["xerr"], Items, axis = 0)
    Raw["Data"]["y"]    = np.delete(Raw["Data"]["y"], Items, axis = 0)
    for item in Raw["Data"]["yerr"]:
        Raw["Data"]["yerr"][item] = np.delete(Raw["Data"]["yerr"][item], Items, axis = 0)

# First put in missing design points
AllMissingPrediction = np.array([])
for Item in DataList:
    if 'PredictionMissing' in Setup['Data'][Item]:
        RawPrediction[Item]['Prediction'] = InsertZeroDesign(RawPrediction[Item]['Prediction'], Setup['Data'][Item]['PredictionMissing'])
        RawPredictionError[Item]['Prediction'] = InsertZeroDesign(RawPredictionError[Item]['Prediction'], Setup['Data'][Item]['PredictionMissing'])
        AllMissingPrediction = np.append(AllMissingPrediction, Setup['Data'][Item]['PredictionMissing'])
AllMissingPrediction = np.sort(AllMissingPrediction)
AllMissingPrediction = np.unique(AllMissingPrediction)

# Then we issue warning if some of them are found to have incompatible design point count
FirstItemSize = -1
for Item in DataList:
    if FirstItemSize < 0:
        FirstItemSize = RawPrediction[Item]['Prediction'].shape[0]
    elif RawPrediction[Item]['Prediction'].shape[0] != FirstItemSize:
        print(f'Warning: {Item} has wrong number of design points')
    elif RawPredictionError[Item]['Prediction'].shape[0] != FirstItemSize:
        print(f'Warning: {Item} has wrong number of design points for errors')

# Clean up points
for Item in DataList:
    if 'DataExclude' in Setup['Data'][Item]:
        DeleteRawData(RawData[Item], Setup['Data'][Item]['DataExclude'])
    if 'PredictionExclude' in Setup['Data'][Item]:
        RawPrediction[Item]["Prediction"] = np.delete(RawPrediction[Item]["Prediction"], Setup['Data'][Item]['PredictionExclude'], axis = 1)
        RawPredictionError[Item]["Prediction"] = np.delete(RawPredictionError[Item]["Prediction"], Setup['Data'][Item]['PredictionExclude'], axis = 1)

# Clean up low/high energy points
if 'DataCut' in Setup and 'MinPT' in Setup['DataCut']:
    for Item in DataList:
        DeleteCount = sum(i < Setup['DataCut']['MinPT'] for i in RawData[Item]["Data"]["x"])
        DeleteRawData(RawData[Item], range(0, DeleteCount))
        RawPrediction[Item]['Prediction'] = np.delete(RawPrediction[Item]["Prediction"], range(0, DeleteCount), axis = 1)
        RawPredictionError[Item]['Prediction'] = np.delete(RawPredictionError[Item]["Prediction"], range(0, DeleteCount), axis = 1)

if 'DataCut' in Setup and 'MaxPT' in Setup['DataCut']:
    print("MaxPT " + str(Setup["DataCut"]["MaxPT"]) + "detected.")
    for Item in DataList:
        DeleteCount = sum(i > Setup['DataCut']['MaxPT'] for i in RawData[Item]["Data"]["x"])
        Size = len(RawData[Item]["Data"]["x"])
        DeleteRawData(RawData[Item], range(Size - DeleteCount, Size))
        RawPrediction[Item]['Prediction'] = np.delete(RawPrediction[Item]["Prediction"], range(Size - DeleteCount, Size), axis = 1)
        RawPredictionError[Item]['Prediction'] = np.delete(RawPredictionError[Item]["Prediction"], range(Size - DeleteCount, Size), axis = 1)


# If some items do not survive the low/high energy cut, remove them from the list
EmptyList = []
for Item in DataList:
    if len(RawData[Item]['Data']['x']) == 0:   # nothing survives!
        EmptyList.append(Item)
DataList = [Item for Item in DataList if Item not in EmptyList]

# Delete prediction that are longer than available design points
NDesign = RawDesign['Design'].shape[0]
for Item in DataList:
    if RawPrediction[Item]['Prediction'].shape[0] > NDesign:
        ToDelete = RawPrediction[Item]['Prediction'].shape[0] - NDesign
        RawPrediction[Item]['Prediction'] = np.delete(RawPrediction[Item]['Prediction'], range(NDesign, RawPrediction[Item]['Prediction'].shape[0]), axis = 0)
    if RawPredictionError[Item]['Prediction'].shape[0] > NDesign:
        ToDelete = RawPredictionError[Item]['Prediction'].shape[0] - NDesign
        RawPredictionError[Item]['Prediction'] = np.delete(RawPredictionError[Item]['Prediction'], range(NDesign, RawPredictionError[Item]['Prediction'].shape[0]), axis = 0)

# Remove bad design points, including the padded ones that some files are missing
InputDesignCount = RawDesign['Design'].shape[0]
ListToDelete = np.array([int(x) for x in Setup['Design']['ListToDelete'] if x < InputDesignCount])
ListToDelete = np.append(ListToDelete, [x for x in AllMissingPrediction if x < InputDesignCount])
ListToDelete = np.sort(ListToDelete)
ListToDelete = np.unique(ListToDelete)
ListToDelete = [int(x) for x in ListToDelete]
# print(ListToDelete)
DesignIndex = np.delete(range(0, InputDesignCount), ListToDelete)

if 'PoorManQALimit' in Setup['Design']:
    minimum = 227 # not all the prection has exactly 230 points for 230106 yaml
    zscores = {}
    for Item in DataList:
        zscores[Item]=stats.zscore(RawPrediction[Item]['Prediction'], axis=0)
    for I in DesignIndex:
        for Item in DataList:
            if I >= minimum or max(RawPrediction[Item]['Prediction'][I,:]) > Setup['Design']['PoorManQALimit'] or any(np.abs(zscores[Item][I,:]) > Setup['Design']['PoorManQALimitZScore']):
            #if I >= minimum or max(RawPrediction[Item]['Prediction'][I,:]) > Setup['Design']['PoorManQALimit']:
                ListToDelete.append(I)
                break
    ListToDelete.sort()
print(len(ListToDelete))

RawDesignIndex = list(range(len(RawDesign['Design'])))
RawDesign['Design'] = np.delete(RawDesign['Design'], ListToDelete, axis = 0)

DesignIndex = np.delete(range(0, InputDesignCount), ListToDelete)
#del RawDesignIndex[ListToDelete]
RawDesignIndex = [x for x in RawDesignIndex if x not in ListToDelete]

picked_indices = [46, 115, 75, 92, 22, 104, 28, 120, 154, 93]

original_indices = [RawDesignIndex[i] for i in picked_indices]

print(original_indices)
