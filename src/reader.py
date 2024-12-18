'''
Read data according to the JetScape 1.0 stat specification
'''

import numpy as np

import os
import pickle
from pathlib import Path


def ReadDesign(FileName):
    # This is the output object
    Result = {}
    Version = ''

    Result["FileName"] = FileName

    # First read all the header information
    with open(FileName, "r") as f:
        for Line in f:
            Items = Line.split()
            if (len(Items) < 2): continue
            if Items[0] != '#': continue

            if(Items[1] == 'Version'):
                Version = Items[2]
            elif(Items[1] == 'Parameter'):
                Result["Parameter"] = Items[2:]

    if(Version not in ['1.0', '2.0']):
        raise AssertionError('Bad file version number while reading design points')

    # Then read the actual design parameters
    Result["Design"] = np.loadtxt(FileName)
    return Result

def ReadData(FileName):
    # Initialize objects
    Result = {}
    Version = ''

    Result["FileName"] = FileName

    # First read all the header information
    print(FileName)
    with open(FileName, "r") as f:
        for Line in f:
            Items = Line.split()
            if (len(Items) < 2): continue
            if Items[0] != '#': continue

            if(Items[1] == 'Version'):
                Result['Version'] = Items[2]
            elif(Items[1] == 'DOI'):
                Result["DOI"] = Items[2:]
            elif(Items[1] == 'Source'):
                Result["Source"] = Items[2:]
            elif(Items[1] == 'System'):
                Result["System"] = Items[2]
            elif(Items[1] == 'Centrality'):
                Result["Centrality"] = Items[2:4]
            elif(Items[1] == 'XY'):
                Result["XY"] = Items[2:4]
            elif(Items[1] == 'Label'):
                Result["Label"] = Items[2:]
            else:
                if 'ExtraComment' not in Result:
                    Result['ExtraComment'] = []
                Result["ExtraComment"].append(Line[2:])

    if(Result['Version'] not in ['1.0', '2.0', '1.1']):
        raise AssertionError('Bad file version number while reading design points')

    XMode = ''
    if Result["Label"][0:4] == ['x', 'y', 'stat,low', 'stat,high']:
        XMode = 'x'
    elif Result["Label"][0:5] == ['xmin', 'xmax', 'y', 'stat,low', 'stat,high']:
        XMode = 'xminmax'
    elif Result["Label"][0:5] == ['xmin', 'xmax', 'y', 'sys,low', 'sys,high']:
        XMode = 'reversedxminmax'
    elif Result["Label"][0:4] == ['xmin', 'xmax', 'y', 'y_err']:
        XMode = 'nosys'
    else:
        raise AssertionError('Invalid list of initial columns!  Should be ("x", "y", "stat,low", "stat,high"), or ("xmin", "xmax", "y", "stat,low", "stat,high")')

    # Then read the actual data
    RawData = np.loadtxt(FileName)

    Result["Data"] = {}
    if(XMode == 'x'):
        Result["Data"]["x"] = RawData[:, 0]
        Result["Data"]["y"] = RawData[:, 1]
        Result["Data"]["yerr"] = {}
        Result["Data"]["yerr"]["stat"] = RawData[:, 2:4]
        Result["Data"]["yerr"]["sys"] = RawData[:, 4:]
        Result["SysLabel"] = Result["Label"][4:]
    elif(XMode == 'xminmax'):
        # If we only have one row of data (eg. CMS Jet RAA, R = 1.0), we need to promote the array
        # from being treated as 1D to being treated as 2D with one row.
        if RawData.ndim == 1:
            RawData = RawData[np.newaxis, :]

        max_label = len(RawData[0])
        Result["Data"]["x"] = (RawData[:, 0] + RawData[:, 1]) / 2
        Result["Data"]["xerr"] = (RawData[:, 1] - RawData[:, 0]) / 2
        Result["Data"]["y"] = RawData[:, 2]
        Result["Data"]["yerr"] = {}
        Result["Data"]["yerr"]["stat"] = RawData[:, 3:5]
        Result["Data"]["yerr"]["sys"] = RawData[:, 5:]
        Result["SysLabel"] = Result["Label"][5:max_label]
        print(Result["SysLabel"])
    elif(XMode == 'reversedxminmax'):
        # If we only have one row of data (eg. CMS Jet RAA, R = 1.0), we need to promote the array
        # from being treated as 1D to being treated as 2D with one row.
        if RawData.ndim == 1:
            RawData = RawData[np.newaxis, :]

        max_label = len(RawData[0])
        Result["Data"]["x"] = (RawData[:, 0] + RawData[:, 1]) / 2
        Result["Data"]["xerr"] = (RawData[:, 1] - RawData[:, 0]) / 2
        Result["Data"]["y"] = RawData[:, 2]
        Result["Data"]["yerr"] = {}
        Result["Data"]["yerr"]["stat"] = RawData[:, 5:7]
        Result["Data"]["yerr"]["sys"] = np.hstack((RawData[:, 3:5], RawData[:, 7:]))
        Result["SysLabel"] = list(np.hstack((Result["Label"][3:5], Result["Label"][7:max_label])))
        print(Result["SysLabel"])
    elif(XMode == 'nosys'):
        if RawData.ndim == 1:
            RawData = RawData[np.newaxis, :]
        Result["Data"]["x"] = (RawData[:, 0] + RawData[:, 1]) / 2
        Result["Data"]["xerr"] = (RawData[:, 1] - RawData[:, 0]) / 2
        Result["Data"]["y"] = RawData[:, 2]
        Result["Data"]["yerr"] = {}
        Result["Data"]["yerr"]["sum"] = RawData[:,[3,3]]
        Result["SysLabel"] = ['','']

    return Result

def WriteData(FileName, Item):
    XMode = ''
    if Item["Label"][0:4] == ['x', 'y', 'stat,low', 'stat,high']:
        XMode = 'x'
    elif Item["Label"][0:5] == ['xmin', 'xmax', 'y', 'stat,low', 'stat,high']:
        XMode = 'xminmax'

    # Assemble header information
    Header = []
    if 'Version' in Item:        Header.append('Version ' + Item['Version'])
    if 'DOI' in Item:            Header.append('DOI ' + ' '.join(Item['DOI']))
    if 'Source' in Item:         Header.append('Source ' + ' '.join(Item['Source']))
    if 'System' in Item:         Header.append('System ' + Item['System'])
    if 'Centrality' in Item:     Header.append('Centrality ' + ' '.join(Item['Centrality']))
    if 'XY' in Item:             Header.append('XY ' + ' '.join(Item['XY']))
    if 'Label' in Item:          Header.append('Label ' + ' '.join(Item['Label']))
    if 'ExtraComment' in Item:   Header.extend(Item['ExtraComment'])

    # Now assemble the big table
    if XMode == 'x':
        Xs = np.array([Item['Data']['x']])
    else:
        Xs = np.concatenate(([Item['Data']['x'] - Item['Data']['xerr']], [Item['Data']['x'] + Item['Data']['xerr']]), axis = 0)

    if Xs.ndim == 0:
        Xs = Xs[np.newaxis, :]

    if Item['Data']['y'].ndim == 0:
        Ys = np.array(Item['Data']['y'])[np.newaxis, :]
    else:
        Ys = np.array([Item['Data']['y']]).T
    RawData = np.concatenate((Xs.T, Ys, Item['Data']['yerr']['stat'], Item['Data']['yerr']['sys']), axis = 1)

    # Save to file!
    np.savetxt(FileName, RawData, header = '\n'.join(Header))


def ReadCovariance(FileName):
    # Initialize objects
    Result = {}
    Version = ''

    Result["FileName"] = FileName

    # First read all the header information
    with open(FileName, "r") as f:
        for Line in f:
            Items = Line.split()
            if (len(Items) < 2): continue
            if Items[0] != '#': continue

            if(Items[1] == 'Version'):
                Version = Items[2]
            elif(Items[1] == 'Data1'):
                Result["Data1"] = Items[2]
            elif(Items[1] == 'Data2'):
                Result["Data2"] = Items[2]

    if(Version not in ['1.0', '2.0']):
        raise AssertionError('Bad file version number while reading design points')

    # Then read the actual covariance matrix
    Result["Matrix"] = np.loadtxt(FileName)
    return Result

def ReadPrediction(FileName):
    # Initialize objects
    Result = {}
    Version = ''

    Result["FileName"] = FileName

    # First read all the header information
    with open(FileName, "r") as f:
        for Line in f:
            Items = Line.split()
            if (len(Items) < 2): continue
            if Items[0] != '#': continue

            if(Items[1] == 'Version'):
                Version = Items[2]
            elif(Items[1] == 'Data'):
                Result["Data"] = Items[2]
            elif(Items[1] == 'Design'):
                Result["Design"] = Items[2]

    if(Version not in ['1.0', '2.0']):
        raise AssertionError('Bad file version number while reading design points')

    # Then read the actual model predictions
    Result["Prediction"] = np.loadtxt(FileName).T
    if len(Result["Prediction"].shape) == 1:   # 1D
        Result["Prediction"] = Result["Prediction"].reshape(Result["Prediction"].shape[0], 1)
    return Result

def InitializeCovariance(data):
    Result = {}
    for system, content in data.items():
        Result[system] = {}
        Combination = []
        for obs in content:
            for subobs in content[obs]:
                Combination.append((obs, subobs))
        for item1 in Combination:
            Result[system][item1] = {}
            for item2 in Combination:
                Result[system][item1][item2] = None
    return Result

"""
def EstimateCovariance(DataX, DataY, SysLength = {}, SysStrength = {}, ScaleX = True, IgnoreMissing = False)
    DataX          data used for the first index of the output matrix
    DataY          data used for the second index of the output matrix
    SysLength      correlation length, source by source.  One can specify a "default" for sources not listed
                   Negative value indicates that the source is treated as uncorrelated.
                   If "default" is not specified, it is assumed to be -1 (ie., uncorrelated)
    SysStrength    correlation strength, source by source.  Again there is a "default" one can specify
                   If "default" is not specified, it is assumed to be 1.0
    ScaleX         whether correlation length is in units of "range of x axis", or units of "x"
    IgnoreMissing  set to true to ignore sources not explicitly listed in SysLength dictionary

Estimates covariance matrix for a block

The function returns a 2D matrix with size (DataX points, DataY points)
If we pass the same thing to DataX and DataY, we can calculate the diagonal blocks.

The formula used to populate the matrix is
   Strength * Sigma_x * Sigma_y * exp(pow(-|x - y| / Length, 1.9))
for each source, and the summed up for all considered sources

Currently only symmetric uncertainties are supported.  If a source ends with ",low" it is ignored and assumed to be covered by a corresponding one ending with ",high"
"""
def EstimateCovariance(DataX, DataY, SysLength = {}, SysStrength = {}, ScaleX = True, IgnoreMissing = False):
    # Number of entries in each data
    NX = len(DataX["Data"]["x"])
    NY = len(DataY["Data"]["x"])

    # Scale of x
    # If ScaleX is true, the correlation length is in units of "x range"
    #    otherwise it's the same unit as "x"
    DX = 1
    DY = 1
    if ScaleX == True:
        # If there is only one row, this will cause issues.
        if len(DataX["Data"]["x"]) > 1:
            DX = 1 / (max(DataX["Data"]["x"]) - min(DataX["Data"]["x"]))
        if len(DataY["Data"]["x"]) > 1:
            DY = 1 / (max(DataY["Data"]["x"]) - min(DataY["Data"]["x"]))

    # Initialize empty matrix
    Matrix = np.zeros([NX, NY])

    # Add statistical uncertainty here, if this is diagonal block
    DiagonalBlock = False
    if DataX["FileName"] == DataY["FileName"]:
        DiagonalBlock = True
        try:
            for i in range(0, NX):
                Matrix[i, i] = Matrix[i, i] + DataX["Data"]["yerr"]["stat"][i][0]**2
        except KeyError:
            for i in range(0, NX):
                Matrix[i, i] = Matrix[i, i] + (DataX["Data"]["y"][i]*0.01)**2

    # Add a default behavior if not supplied already
    if "default" not in SysLength:
        SysLength["default"] = -1
    if "default" not in SysStrength:
        SysStrength["default"] = 1.0

    # Now loop over systematic source in dataX, and check if the same thing exist in dataY
    print(DataX["SysLabel"])
    for Source in DataX["SysLabel"]:
        if ",low" in Source:
            continue
        if Source not in DataY["SysLabel"]:
            continue

        if (IgnoreMissing == True) and (Source not in SysLength):
            continue

        IX = DataX["SysLabel"].index(Source)
        IY = DataY["SysLabel"].index(Source)

        print(DataX["SysLabel"], DataY["SysLabel"], IX, IY)

        Length = SysLength.get(Source, SysLength["default"])
        Strength = SysStrength.get(Source, SysStrength["default"])

        for x in range(0, NX):
            for y in range(0, NY):
                Factor = 0
                if(Length > 0):   # Correlated
                    Diff = DataX["Data"]["x"][x] * DX - DataY["Data"]["x"][y] * DY
                    Factor = np.exp(-np.power(np.absolute(Diff) / Length, 1.9));
                else:             # Non-correlated
                    if DiagonalBlock == True:
                        Factor = (x == y)
                Factor = Factor * Strength
                try:
                    Matrix[x, y] = Matrix[x, y] + DataX["Data"]["yerr"]["sys"][x][IX] * DataY["Data"]["yerr"]["sys"][y][IY] * Factor
                except KeyError:
                    Matrix[x, y] = Matrix[x, y] + DataX["Data"]["yerr"]["sum"][x][IX] * DataY["Data"]["yerr"]["sum"][y][IY] * Factor

    return Matrix
