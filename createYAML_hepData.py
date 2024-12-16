import sys,yaml,glob,re,fnmatch

## read the yaml config from JETSCAPE-analysis package and write in the format that compatible to the STAT code

file_path = '../../jetscape-docker/JETSCAPE-analysis/config/STAT_5020.yaml'
#file_path = '../../jetscape-docker/JETSCAPE-analysis/config/STAT_2760.yaml'
#file_path = '../../jetscape-docker/JETSCAPE-analysis/config/STAT_200.yaml'

# Open and load the YAML file
with open(file_path, 'r') as file:
    yaml_data = yaml.safe_load(file)

## as of Nov 12 2024, these are included and calculated in JETSCAPE-analysis
if '5020' in file_path:
    obs_type={'hadron':['pt_ch_alice', 'pt_pi_alice', 'pt_ch_cms'],
              'inclusive_jet':['pt_alice', 'pt_atlas', 'pt_cms', 'Dz_atlas', 'Dpt_atlas', 'zg_cms'],
              'inclusive_chjet':['zg_alice', 'tg_alice']}
elif '2760' in file_path:
    obs_type={'hadron':['pt_ch_alice', 'pt_pi_alice', 'pt_pi0_alice', 'pt_ch_atlas', 'pt_ch_cms'],
              'inclusive_jet':['pt_alice', 'pt_atlas', 'pt_cms', 'Dz_atlas', 'Dpt_atlas', 'Dz_cms', 'Dpt_cms']}
              #'inclusive_chjet':['pt_alice']}
    # Dz and Dpt cms hepdata doesn't exist. (too old? published in 2014)
elif '200' in file_path:
    obs_type={'hadron':['pt_pi0_phenix', 'pt_ch_star'],
              'inclusive_chjet':['pt_star']}

#obs_type={'hadron':['pt_ch_alice', 'pt_pi_alice', 'pt_ch_cms']}

d = {}
for obs in obs_type.keys():
    d[f'hepdata_{obs}'] = {} 
    d[f'hepdata_{obs}']['filepath'] = 'input/analysis24-test/'
    d[f'hepdata_{obs}']['data_vrs'] = 'Version 2.0'
    d[f'hepdata_{obs}']['data_str'] = 'Data'
    d[f'hepdata_{obs}']['data_url'] = []
    d[f'hepdata_{obs}']['data_doi'] = []
    d[f'hepdata_{obs}']['data_fig'] = []
    d[f'hepdata_{obs}']['data_exp'] = []
    d[f'hepdata_{obs}']['data_sys'] = []
    d[f'hepdata_{obs}']['data_meas'] = []
    d[f'hepdata_{obs}']['data_cent'] = []
    d[f'hepdata_{obs}']['data_year'] = []
    d[f'hepdata_{obs}']['data_pt'] = []
    d[f'hepdata_{obs}']['data_r'] = []
    d[f'hepdata_{obs}']['data_joker'] = []
    d[f'hepdata_{obs}']['data_fname'] = []
    print(obs)
    if obs == 'hadron':
        for k in yaml_data[obs].keys():
            if k not in obs_type[obs]: continue
            ana = yaml_data[obs][k]
            length = (len(ana['pt'])-1)*len(ana['centrality'])
            for i in range(length):
                if isinstance(ana['hepdata_AA_dir'], list): table=ana['hepdata_AA_dir'][i].replace(' ','')
                else: table=ana['hepdata_AA_dir'].replace(' ','')
                pattern = r'ins\d+'
                try:
                    ins = re.search(pattern, ana['hepdata']).group()
                except:
                    print("Missing hepdata link for:", k)
                    continue
                url = f'https://www.hepdata.net/download/table/{ins}/{table}/yaml'
                experimentReg = r'cms|atlas|alice|phenix|star'
                experiment = re.findall(experimentReg, k)[0].upper()
                comReg = r'200|2760|5020'
                com = re.findall(comReg,file_path)[0]
                sys = 'PbPb'
                system = f'{sys}{com}'
                cent_low = ana['centrality'][i][0]
                cent_high = ana['centrality'][i][1]
                d[f'hepdata_{obs}']['data_url']+=[url]
                d[f'hepdata_{obs}']['data_doi']+=['']
                d[f'hepdata_{obs}']['data_fig']+=['']
                d[f'hepdata_{obs}']['data_exp']+=[experiment]
                d[f'hepdata_{obs}']['data_sys']+=[system]
                d[f'hepdata_{obs}']['data_meas']+=['RAA']
                d[f'hepdata_{obs}']['data_cent']+=[f'{cent_low}to{cent_high}']
                d[f'hepdata_{obs}']['data_year']+=['']
                d[f'hepdata_{obs}']['data_pt']+=['']
                d[f'hepdata_{obs}']['data_r']+=['']
                d[f'hepdata_{obs}']['data_joker']+=['']
                d[f'hepdata_{obs}']['data_fname']+=[f'Data__{com}__{sys}__{obs}__{k}____{cent_low}-{cent_high}.dat']

    else:
        for k in yaml_data[obs].keys():
            if k not in obs_type[obs]: continue
            ana = yaml_data[obs][k]
            #length = len(ana['jet_R'])*(len(ana['pt'])-1)*len(ana['centrality'])
            pattern = 'hepdata_AA_dir*'
            entries = {key: value for key, value in ana.items() if fnmatch.fnmatch(key, pattern)}
            print(k, entries)
            for entry in entries:
                print('entry',entry)
                pattern = r'ins\d+'
                try:
                    ins = re.search(pattern, ana['hepdata']).group()
                except:
                    print("Missing hepdata link for:", k)
                    continue
                experimentReg = r'cms|atlas|alice|phenix|star'
                experiment = re.findall(experimentReg, k)[0].upper()
                comReg = r'200|2760|5020'
                com = re.findall(comReg,file_path)[0]
                sys = 'PbPb'
                system = f'{sys}{com}'
                if isinstance(ana[entry], list) and len(ana[entry])>1:
                    for i in range(len(ana[entry])):
                        table=ana[entry][i].replace(' ','')
                        if table: url = f'https://www.hepdata.net/download/table/{ins}/{table}/yaml'
                        else: url = ''
                        pattern = r'pt\d+'
                        try: pt = re.search(pattern, entry).group()
                        except: pt=''
                        pattern = r'R\d+\.\d+'
                        try: r = re.search(pattern, entry).group()
                        except: r=''
                        j = entry.replace('hepdata_AA_dir_','')
                        cent = ana['centrality'][i]
                        print(entry, table, pt, r, j, cent, url)
                        cent_low = ana['centrality'][i][0]
                        cent_high = ana['centrality'][i][1]
                        d[f'hepdata_{obs}']['data_url']+=[url]
                        d[f'hepdata_{obs}']['data_doi']+=['']
                        d[f'hepdata_{obs}']['data_fig']+=['']
                        d[f'hepdata_{obs}']['data_exp']+=[experiment]
                        d[f'hepdata_{obs}']['data_sys']+=[system]                              
                        d[f'hepdata_{obs}']['data_meas']+=['RAA']
                        d[f'hepdata_{obs}']['data_cent']+=[f'{cent_low}to{cent_high}']
                        d[f'hepdata_{obs}']['data_year']+=['']
                        d[f'hepdata_{obs}']['data_pt']+=[pt]
                        d[f'hepdata_{obs}']['data_r']+=[r]
                        d[f'hepdata_{obs}']['data_joker']+=[j]
                        d[f'hepdata_{obs}']['data_fname']+=[f'Data__{com}__{sys}__{obs}__{k}__{j}__{cent_low}-{cent_high}.dat']
                        print(f'Data__{com}__{sys}__{obs}__{k}__{j}__{cent_low}-{cent_high}.dat')
                elif (isinstance(ana[entry], list) and len(ana[entry])==1) or not isinstance(ana[entry], list):
                    
                    if "hepdata_AA_gname" in ana.keys():
                        for i in range(len(ana['hepdata_AA_gname'])):
                            table=ana[entry].replace(' ','')
                            if table: url = f'https://www.hepdata.net/download/table/{ins}/{table}/yaml'
                            else: url = ''
                            pattern = r'pt\d+'
                            try: pt = re.search(pattern, entry).group()
                            except: pt=''
                            pattern = r'R\d+\.\d+'
                            try: r = re.search(pattern, entry).group()
                            except: r=''
                            j = entry.replace('hepdata_AA_dir_','')
                            cent = ana['centrality'][i]
                            print(entry, table, pt, r, j, cent, url)
                            cent_low = ana['centrality'][i][0]
                            cent_high = ana['centrality'][i][1]
                            d[f'hepdata_{obs}']['data_url']+=[url]
                            d[f'hepdata_{obs}']['data_doi']+=['']
                            d[f'hepdata_{obs}']['data_fig']+=['']
                            d[f'hepdata_{obs}']['data_exp']+=[experiment]
                            d[f'hepdata_{obs}']['data_sys']+=[system]                              
                            d[f'hepdata_{obs}']['data_meas']+=['RAA']
                            d[f'hepdata_{obs}']['data_cent']+=[f'{cent_low}to{cent_high}']
                            d[f'hepdata_{obs}']['data_year']+=['']
                            d[f'hepdata_{obs}']['data_pt']+=[pt]
                            d[f'hepdata_{obs}']['data_r']+=[r]
                            d[f'hepdata_{obs}']['data_joker']+=[j]
                            d[f'hepdata_{obs}']['data_fname']+=[f'Data__{com}__{sys}__{obs}__{k}__{j}__{cent_low}-{cent_high}.dat']
                            print(f'Data__{com}__{sys}__{obs}__{k}__{j}__{cent_low}-{cent_high}.dat')
                    elif entry.replace('dir','gname') in ana.keys():
                        for i in range(len(ana[entry.replace('dir','gname')])):
                            table=ana[entry].replace(' ','')
                            if table: url = f'https://www.hepdata.net/download/table/{ins}/{table}/yaml'
                            else: url = ''
                            pattern = r'pt\d+'
                            try: pt = re.search(pattern, entry).group()
                            except: pt=''
                            pattern = r'R\d+\.\d+'
                            try: r = re.search(pattern, entry).group()
                            except: r=''
                            j = entry.replace('hepdata_AA_dir_','')
                            cent = ana['centrality'][i]
                            print(entry, table, pt, r, j, cent, url)
                            cent_low = ana['centrality'][i][0]
                            cent_high = ana['centrality'][i][1]
                            d[f'hepdata_{obs}']['data_url']+=[url]
                            d[f'hepdata_{obs}']['data_doi']+=['']
                            d[f'hepdata_{obs}']['data_fig']+=['']
                            d[f'hepdata_{obs}']['data_exp']+=[experiment]
                            d[f'hepdata_{obs}']['data_sys']+=[system]                              
                            d[f'hepdata_{obs}']['data_meas']+=['RAA']
                            d[f'hepdata_{obs}']['data_cent']+=[f'{cent_low}to{cent_high}']
                            d[f'hepdata_{obs}']['data_year']+=['']
                            d[f'hepdata_{obs}']['data_pt']+=[pt]
                            d[f'hepdata_{obs}']['data_r']+=[r]
                            d[f'hepdata_{obs}']['data_joker']+=[j]
                            d[f'hepdata_{obs}']['data_fname']+=[f'Data__{com}__{sys}__{obs}__{k}__{j}__{cent_low}-{cent_high}.dat']
                            print(f'Data__{com}__{sys}__{obs}__{k}__{j}__{cent_low}-{cent_high}.dat')
                            
if '5020' in file_path:
    out_path = 'config/expdata_config_analysis24_5020.yaml'
elif '2760' in file_path:
    out_path = 'config/expdata_config_analysis24_2760.yaml'
elif '200' in file_path:
    out_path = 'config/expdata_config_analysis24_200.yaml'
    
with open(out_path, 'w') as file:
    #yaml.dump(d, file, default_flow_style=None, indent=2)
    yaml.dump(d, file, default_flow_style=None, default_style=None, allow_unicode=True, Dumper=yaml.SafeDumper)
