"""
Fetch data from hepdata (yaml format) and write output files in jetscape-stat format documented
  [location of format specification file goes here]
"""

from urllib.request import urlopen
import re
import sys
import ssl
import yaml
import os
import time
import urllib

#----------------------------------------------------------------------------------------------
def get_hepdata(configFileEntry = None):

  # Check that config file entry exists
  if not configFileEntry:
    print('configFileEntry is empty!')
    return

  # Load configuration variables
  filepath = configFileEntry['filepath']
  data_vrs = configFileEntry['data_vrs']
  data_str = configFileEntry['data_str']
  data_url = configFileEntry['data_url']
  data_doi = configFileEntry['data_doi']
  data_fig = configFileEntry['data_fig']
  data_exp = configFileEntry['data_exp']
  data_sys = configFileEntry['data_sys']
  data_meas = configFileEntry['data_meas']
  data_cent = configFileEntry['data_cent']
  data_year = configFileEntry['data_year']
  data_fname = configFileEntry['data_fname']

  # Create directory for filepath, if it doesn't exist
  if not filepath.endswith('/'):
    filepath = filepath + '/'
  if not os.path.exists(filepath):
    os.makedirs(filepath)

  # KLUDGE-ALERT
  # For this url we need to disable certificates -- find out why don't Jonah's scripts need this
  context = ssl._create_unverified_context()

  for i in list(range(len(data_url))):
    print('------------------')
    print(data_url[i])
    # Create new header for this entry
    data_header = '# Version 1.1\n'
    data_header += '# DOI ' + data_doi[i] + '\n'
    data_header += '# Source ' + data_url[i] + '\n'
    data_header += '# Experiment ' + data_exp[i] + '\n'
    data_header += '# System ' + data_sys[i] + '\n'
    data_header += '# Centrality ' + data_cent[i] + '\n'
    # Fill the remaining header entries from hepdata

    # Reset data lists
    xlo  = []
    xhi  = []
    yval = []
    errs = []

    #print("url:", data_url[i])
    # Fetch yaml_data from hepdata url
    if data_url[i] == '': continue
    try:
      response = urlopen(data_url[i],context=context)
    except urllib.error.HTTPError as e:
      if e.code == 429:  # Too Many Requests
        print("Rate limit exceeded. Waiting...")
        time.sleep(10)  # Wait 10 seconds before retrying
        response = urlopen(data_url[i],context=context)
      else:
        raise
    content  = response.read().decode('utf-8')
    #print("content:\n",content)
    yaml_data = yaml.load(content, Loader=yaml.SafeLoader)

    # Fetch XY names from headers
    xname = yaml_data['independent_variables'][0]['header']['name']
    yname = yaml_data['dependent_variables'][0]['header']['name']
    data_header += '# XY ' + xname + ' ' + yname + '\n'
    
    # Fetch error labels from first entry to create label for header
    error_label = ''
    if len(yaml_data['dependent_variables']) >1:
      for h in range(len(yaml_data['dependent_variables'])):
        #print(h, yaml_data['dependent_variables'][h]['values'])
        block=yaml_data['dependent_variables'][h]['qualifiers']
        index = next((i for i, d in enumerate(block) if d.get('name') == 'Centrality'), None)
        if index==None:
          index = next((i for i, d in enumerate(block) if d.get('name') == 'CENT'), None)
        if index==None:
          index = next((i for i, d in enumerate(block) if d.get('name') == 'CENTRALITY'), None)
        cent = block[index]['value']
        try:
          pattern = r'(\d+)-(\d+)'
          match = re.search(pattern, cent).group()
          cent = match.replace('-','to')
        except:
          cent = cent.replace(' TO ','to').replace('.0','').replace(' pct','')
        if cent == data_cent[i]:
          first_entry = next((entry for entry in yaml_data['dependent_variables'][h]['values'] if entry['value'] != '-'), None)
          print("first_entry:",first_entry)
          print("cent:", cent)
          print("h:", h)
          
          for err in first_entry['errors']:
            error_label += err['label']+',low ' + err['label']+',high '
            data_header +='# Label xmin xmax y ' + error_label + '\n'
        
          for x in yaml_data['independent_variables'][0]['values']:
            xlo.append(x['low'])
            xhi.append(x['high'])
            # print(x['low'],x['high'])
        
          for v in yaml_data['dependent_variables'][h]['values']:
            # print(v['value'])
            yval.append(v['value'])
            errs.append('')
            try:
              for err in (v['errors']):
                try:
                  e = str(err['symerror'])
                  # Convert if percentage
                  if (e[-1]=='%'):
                    e = str(float(e[:-1])*v['value']*0.01)
                  errs[-1] += ' ' + e + ' ' + e
                except KeyError:
                  e = err['asymerror']
                  errs[-1] += ' ' + str(abs(float(e['plus']))) + ' ' + str(abs(float(e['minus'])))
            except KeyError:
              yval[-1] = '0'
              for err in (first_entry['errors']):
                e = '0'
                errs[-1] += ' ' + e + ' ' + e
        
            # Check that we have same number of x and y entries
          try:
            len(xlo)==len(yval)
          except Error:
            message = ' Unequal x and y entries ' + str(len(xlo)) + ' ' + str(len(yval))
            sys.exit(message)
        
          data_lines = ''
          for j in list(range(len(xlo))):
            data_lines += str(xlo[j]) + ' ' + str(xhi[j]) + ' ' + str(yval[j]) + errs[j] + '\n'
    else:
      first_entry = yaml_data['dependent_variables'][0]['values'][0]
      print("first_entry:",first_entry)
      for err in first_entry['errors']:
        error_label += err['label']+',low ' + err['label']+',high '
        data_header +='# Label xmin xmax y ' + error_label + '\n'
       
      # print(yaml_data['independent_variables'][0]['values'])
      for x in yaml_data['independent_variables'][0]['values']:
        xlo.append(x['low'])
        xhi.append(x['high'])
        # print(x['low'],x['high'])
       
      # print(yaml_data['dependent_variables'][0]['values'])
      for v in yaml_data['dependent_variables'][0]['values']:
        # print(v['value'])
        yval.append(v['value'])
       
        errs.append('')
        #print('errors:',v['errors'])
        for err in (v['errors']):
          try:
            e = str(err['symerror'])
            # Convert if percentage
            if (e[-1]=='%'):
              e = str(float(e[:-1])*v['value']*0.01)
            errs[-1] += ' ' + e + ' ' + e
          except KeyError:
            e = err['asymerror']
            errs[-1] += ' ' + str(abs(float(e['plus']))) + ' ' + str(abs(float(e['minus'])))
                # Check that we have same number of x and y entries
      try:
        len(xlo)==len(yval)
      except Error:
        message = ' Unequal x and y entries ' + str(len(xlo)) + ' ' + str(len(yval))
        sys.exit(message)
       
      data_lines = ''
      for j in list(range(len(xlo))):
        data_lines += str(xlo[j]) + ' ' + str(xhi[j]) + ' ' + str(yval[j]) + errs[j] + '\n'
        
    # Create filename
    filename = f'{filepath}{data_fname[i]}'
        
    print('Writing ',filename)
    with open(filename,'w+') as f:
      f.write(data_header)
      f.write(data_lines)
    
#----------------------------------------------------------------------------------------------
if __name__ == '__main__':
  get_hepdata()
