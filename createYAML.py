import sys, yaml, glob,re


d = {}
d["BaseDirectory"] = 'input/STAT20241216Exponential/'

#d['Tag'] = 'STAT20230116ExponentialRBF_JetAndJetDz_CentralityMax10_v5'
#d['Tag'] = 'STAT20230116ExponentialRBF_JetAndJetSub_CentralityMax10_V2'
#d['Tag'] = 'STAT20230116ExponentialRBF_JetDzOnly_CentralityMax10_V10'
#d['Tag'] = 'STAT20230116ExponentialRBF_JetSubOnly_CentralityMax10_V1'
d['Tag'] = 'STAT20241216ExponentialRBF_allCentrality'

d['Emulator']={}
d['Emulator']['NPC'] = 5
d['Emulator']['Kernel'] = 'RBFNoise'
d['Emulator']['NRetrain'] = 50
d['Emulator']['PCACheck'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]

d['MCMC']={}
d['MCMC']['NWalker'] = 50
d['MCMC']['NBurn'] = 5000
d['MCMC']['NStep'] = 100000

d['Design']={}
d['Design']['File'] = 'Design__exponential.dat'
d['Design']['LogScale'] = [2, 3, 5]
d['Design']['ListToDelete'] = []
d['Design']['PoorManQALimit'] = 5
d['Design']['PoorManQALimitZScore'] = 5
d['Design']['Range'] = [[0.1, 0.5],[1, 10],[0.005, 10],[0.005, 10],[0, 1.5],[0.05, 100]]

d["Data"]={}

files = glob.glob("input/STAT20230116Exponential/Data*")

#include = ["_jet__pt_", "_chjet__pt_", "_chjet__tg_", "_chjet__zg_", "_jet__Dz_", "_jet__Dpt_"]
#include = ["_jet__pt_", "_chjet__pt_", "_chjet__tg_", "_chjet__zg_", "_jet__Dz_"]
include = ["_jet__pt_", "_chjet__pt_", "_chjet__tg_", "_chjet__zg_", "_jet__zg_", "_jet__Dz_", "_jet__Dpt_"]
#include = ["_chjet__tg_", "_chjet__zg_", "_jet__zg_", "_jet__Dz_", "_jet__Dpt_"]
#include = ["_jet__Dz_"]
exclude = ["_jet__pt_y_", "_chjet__pt_alice_", "Dz_cms", "Dpt_cms"]

for filename in files:
    
    fil = filename.split('/')[2]
    if not any(obs in filename for obs in include): continue
    if any(obs in filename for obs in exclude): continue
    ifil = fil
    experimentReg = r'cms|atlas|alice|phenix|star'
    experiment = re.findall(experimentReg, fil)[0].upper()
    #print(experiment)
    comReg = r'200|2760|5020'
    com = re.findall(comReg,fil)[0]
    #print(com)

    sysReg = r'PbPb|AuAu'
    sys = re.findall(sysReg,fil)[0]
    #print(sys)

    centralityReg = r'__([0-9]+-[0-9]+)\.dat'
    centrality = re.findall(centralityReg,fil)[0]
    centralityMin = centrality.split('-')[0]
    centralityMax = centrality.split('-')[1]

    #if int(centralityMax) > 10: continue
    

    fil=fil.replace(experiment,'').replace(com,'').replace(sys,'').replace(centrality,'').replace('.dat','').replace(experiment.lower(),'').replace('Data','').replace('.','p').replace('_',' ').split()
    fil = [f.capitalize() for f in fil]
    observable = ''.join(fil)

    #if "Charge" in observable or "JetMg" in observable or "ChjetGR" in observable or "ChjetPtd" in observable or "Hadron" in observable or "Dijet" in observable or "JetPtY" in observable or int(centralityMax) > 50: continue

    #if int(centralityMax) > 10: continue
    print(filename)

    name = '{}_{}_{}_{}_{}'.format(experiment,com,observable,centralityMin,centralityMax)
    d["Data"][name]={}

    attribute={}
    attribute["Energy"]=com
    attribute["Observable"]=observable
    attribute["CentralityMin"]=centralityMin
    attribute["CentralityMax"]=centralityMax

    d["Data"][name]['Attribute']=attribute
    d["Data"][name]['Data']=ifil
    d["Data"][name]['DataExclude']=[]
    d["Data"][name]['Prediction']=ifil.replace('Data','Prediction__exponential').replace('.dat','__values.dat')
    d["Data"][name]['PredictionError']=ifil.replace('Data','Prediction__exponential').replace('.dat','__errors.dat')
    d["Data"][name]['Correlation']={}

file_path = 'yaml/{}.yaml'.format(d['Tag'])

with open(file_path, 'w') as file:
    yaml.dump(d, file, default_flow_style=False, indent=3)

    
    
    
    
