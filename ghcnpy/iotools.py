# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %matplotlib inline

# +
# Import Modules
import re
import os
import sys
from ftplib import FTP
# from progressbar import ProgressBar, Bar, ETA, FileTransferSpeed, Percentage
import datetime
from datetime import date
import time

import numpy as np
import pandas as pd
# import netCDF4 as nc

# -

# MODULE: get_ghcnd_version
# Get which version of GHCN-D we are using
# ################################################
def get_ghcnd_version():

    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    ftp.cwd('pub/data/ghcn/daily')
    ftp.retrbinary('RETR ghcnd-version.txt', open('ghcnd-version.txt', 'wb').write)
    ftp.quit()

    ghcnd_versionfile='ghcnd-version.txt'
    try:
        with open (ghcnd_versionfile, "r") as myfile:
            ghcnd_version=myfile.read().replace('\n', '')
    except:
        print(("Version file does not exist: ",ghcnd_versionfile))
        sys.exit()

    return ghcnd_version


# MODULE: get_data_station
# Fetch Individual station (.dly ASCII format)
# ################################################

# +
# def file_write(data):
#     file.write(data) 
#     global pbar
#     pbar += len(data)
#     return None

# +
def get_data_station(station_id):
    """Fetch Individual station (.dly ASCII format)"""
    
    data_station_path = station_id+'.dly'

    if not os.path.isfile(data_station_path):
#     if not os.path.isfile(file):   
        print("DOWNLOADING DATA FOR STATION: " + station_id)
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/ghcn/daily/all')

        
        ftp.retrbinary('RETR ' + data_station_path, open(data_station_path, 'wb').write)
        ftp.quit()

#     if not os.path.isfile(data_station_path):           
#         print("DOWNLOADING DATA FOR STATION: " + station_id)
#         data_station_file = open(data_station_path, 'wb')
#         ftp = FTP('ftp.ncdc.noaa.gov')
#         ftp.login()
#         ftp.cwd('pub/data/ghcn/daily/all')
        
#         ftp.sendcmd("TYPE i")    # Switch to Binary mode
#         size = ftp.size(data_station_path) 
#         print(size)
        
#         widgets = ['Downloading: ', Percentage(), ' ',
#                         Bar(marker='#',left='[',right=']'),
#                         ' ', ETA(), ' ', FileTransferSpeed()]

#         pbar = ProgressBar(widgets=widgets, maxval=size)
#         pbar.start()
        
#         ftp.retrbinary('RETR ' + data_station_path, file_write)
#         ftp.quit()
        

    mtime = time.strftime('%Y-%m-%D %H:%M:%S',time.localtime(os.path.getmtime(data_station_path)))
    print("Output from local file: {} - Last modified: {}".format(data_station_path, mtime))
    
    return data_station_path


# -

def get_data_year(year):
    """Fetch 1 Year of Data (.csv ASCII format)"""
    print(("\nGETTING DATA FOR YEAR: ",year))

    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    ftp.cwd('pub/data/ghcn/daily/by_year')
    ftp.retrbinary('RETR '+year+'.csv.gz', open(year+'.csv.gz', 'wb').write)
    ftp.quit()

    outfile=year+".csv.gz"
    return outfile

def get_ghcnd_stations():
    """Read or download GHCND-D Stations File"""

    ghcnd_stnfile='ghcnd-stations.txt'    
    
    if not os.path.isfile(ghcnd_stnfile):
        print("DOWNLOADING LATEST STATION METADATA FILE")
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/ghcn/daily')
        ftp.retrbinary('RETR ghcnd-stations.txt', open('ghcnd-stations.txt', 'wb').write)
        ftp.quit()
    
    mtime = time.strftime('%Y-%m-%D %H:%M:%S',time.localtime(os.path.getmtime(ghcnd_stnfile)))
    print("Output from local file: {} - Last modified: {}".format(ghcnd_stnfile, mtime))
    
    ghcnd_stations = np.genfromtxt(ghcnd_stnfile,delimiter=(11,9,10,7,4,30),dtype=str)
    
    return ghcnd_stations

def get_ghcnd_inventory():
    print("\nGRABBING LATEST STATION INVENTORY FILE")

    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    ftp.cwd('pub/data/ghcn/daily')
    ftp.retrbinary('RETR ghcnd-inventory.txt', open('ghcnd-inventory.txt', 'wb').write)
    ftp.quit()

    # Read in GHCND-D INVENTORY File
    ghcnd_invfile='ghcnd-inventory.txt'
    ghcnd_inventory= np.genfromtxt(ghcnd_invfile,delimiter=(11,9,11,4),dtype=str)

    return ghcnd_inventory

def output_to_csv(station_id):
    
    # Elements of GHCN-D as CODE: [index, divisor]
    elem_dict = {'TMAX':[0,10],
               'TMIN':[1,10],
               'PRCP':[2,10],
               'SNOW':[3,1],
               'SNWD':[4,1],
               'AWND':[5,10],
               'EVAP':[6,10],
               'MNPN':[7,10],
               'MXPN':[8,10],
               'PSUN':[9,1],
               'TSUN':[10,1],          
                }
    num_elements = len(elem_dict)

    # Read in GHCN-D Data
    infile = station_id+".dly"

    try:
        print("Reading local copy of file: {}".format(infile))
        file_handle = open(infile, 'r')
        ghcnd_contents = file_handle.readlines()
        file_handle.close()
    except:
        print("File {} not found in current working directory...".format(infile))
        get_data_station(station_id)
        file_handle = open(infile, 'r')
        ghcnd_contents = file_handle.readlines()
        file_handle.close()

    # Get Year Start and End of File for time dimensions
    ghcnd_begin_year =  int(ghcnd_contents[0][11:15])
    ghcnd_end_year = int(ghcnd_contents[len(ghcnd_contents)-1][11:15])
    num_years = int((ghcnd_end_year - ghcnd_begin_year) + 1)

    # initialize array with -9999 values, as this is the format used to represent missing values
    # will convert -9999 to np.nan later
    ghcnd_data= np.zeros((num_years,12,31,num_elements),dtype='f')-(9999.0)
    
    # Go through GHCN-D Data
    for counter in range(len(ghcnd_contents)): 
        # station ID is first 11 characters
        # year starts on character 12 (or 11 when you count from zero!)  
        year = int(ghcnd_contents[counter][11:15])
        month = int(ghcnd_contents[counter][15:17])

        year_counter = int(year - ghcnd_begin_year)
        month_counter = int(month - 1)

        # element is defined in char 18-21 = 17-20 counting from 0 or 17:21 in slice
        element = ghcnd_contents[counter][17:21]
        if element in elem_dict:
            element_idx = elem_dict[element][0]
            divisor = elem_dict[element][1]
            char=21 # starting character of first VALUE daily data entries in .dly file

            # always use 31 days per .dly file spec
            for day_counter in range(0,31): 
                ghcnd_data[year_counter,month_counter,day_counter,element_idx] = float(ghcnd_contents[counter][char:char+5]) / divisor
                char = char + 8 # each daily entry is 8 characters long, 5 for value and 3 for quality codes
    

    # Format header for csv file
    header_string = "YYYY,MM,DD"
    for key in elem_dict.keys():
        header_string = header_string + "," + key
    header_string = header_string + "\n"  
    
    # Write data to csv file
    print("OUTPUTTING TO CSV: " + station_id + ".csv")
    outfile_data = station_id+'.csv'
    out_data = open(outfile_data,'w')
    out_data.write(header_string)

    for year_counter in range(0,num_years):
        year_str = str(year_counter+ghcnd_begin_year)
        for month_counter in range(0,12):
            month_str = str(month_counter+1)
            for day_counter in range(0,31):
                day_str = str(day_counter+1)              
#                 day_string = year_str + "-" + month_str + "-" + day_str
                day_string = year_str + "," + month_str + "," + day_str
                for elem_key, elem_val in elem_dict.items():
                        day_string = day_string + "," + str(ghcnd_data[year_counter,month_counter,day_counter,elem_val[0]])
                day_string += "\n"
                out_data.write(day_string)

    out_data.close()
    return None


def csv_to_dataframe(station_id):
    
    station_id_file = station_id + ".csv"
    try:
        df = pd.read_csv(station_id_file)
    except:
        print("csv file not found in local directory...")
        output_to_csv(station_id)
        df = pd.read_csv(station_id_file)
        
    df.where(df > -998, other=np.nan, errors='ignore', inplace=True)
    df.dropna(how='all', axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df['YYYY'].astype(str) + ' ' + df['MM'].astype(str) + ' ' + df['DD'].astype(str), errors='coerce')
    df['Date'].where(df['Date'] < datetime.datetime.now(), other=pd.NaT, inplace=True)
    df.dropna(how='any', axis=0, inplace=True, subset=['Date'])
    df.set_index('Date', inplace=True)
    return df
