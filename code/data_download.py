"""Functions used to download and input csv and nc files from https://data.giss.nasa.gov/gistemp/"""

author = 'Rick Forest'

import os
import requests
import datetime
import glob
import gzip
import pandas as pd
import xarray as xr

def download_csv(data_dir, file_id):
    
    # build url, download file using url, 
    giss_url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/"
    file_name = file_id + ".Ts+dSST.csv"
    file_url = giss_url + file_name   
    
    # save file to data directory
    save_file_path = os.path.join(data_dir, file_name)
        
    # get url last modified date and time
    r = requests.head(file_url)
    url_time_str = r.headers['last-modified']
    url_datetime = datetime.datetime.strptime(url_time_str , "%a, %d %b %Y %X %Z")
    url_timestamp = datetime.datetime.timestamp(url_datetime)
    
    # get file last downloaded timestamp if exists, if not set to 0
    if os.path.exists(save_file_path):
        file_timestamp = os.path.getmtime(save_file_path)
    else:
        file_timestamp = 0

    # compare url and file timestamps, if url is greater than download new file    
    if url_timestamp > file_timestamp:     
        r = requests.get(file_url)
        open(save_file_path, 'wb').write(r.content)
        print('downloaded new update:', datetime.date.fromtimestamp(url_timestamp))
    else:
        print('current file is latest', datetime.date.fromtimestamp(file_timestamp))
        
def download_nc(data_dir):
    
    # build url, download file using url, 
    file_url = "https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz"  
    file_name = "gistemp1200_GHCNv4_ERSSTv5.nc"
    
    # save file to data directory
    save_file_path = os.path.join(data_dir, file_name)
        
    # get url last modified date and time
    r = requests.head(file_url)
    url_time_str = r.headers['last-modified']
    url_datetime = datetime.datetime.strptime(url_time_str , "%a, %d %b %Y %X %Z")
    url_timestamp = datetime.datetime.timestamp(url_datetime)
    
    # get file last downloaded timestamp if exists, if not set to 0
    if os.path.exists(save_file_path):
        file_timestamp = os.path.getmtime(save_file_path)
    else:
        file_timestamp = 0

    # compare url and file timestamps, if url is greater than download new file    
    if url_timestamp > file_timestamp:     
        r = requests.get(file_url)
        open(save_file_path, 'wb').write(r.content)
        print('downloaded new update:', datetime.date.fromtimestamp(url_timestamp))
    else:
        print('current file is latest', datetime.date.fromtimestamp(file_timestamp))

def directory_catalog(data_directory, file_type):
    """For input data_directory:
       - creating a list of csv files contained in directory
       - add size dimensions for each file
    
    Parameters
    ----------
    data_directory : str
        Path of data folder containing data directories.
    file_type : str
        Type of file to cataloge (csv, nc)

    Returns
    ------
    catalog_df : dataframe
        csv: directory name, file name, tuple of (rows, columns)
        nc: directory name, file name, dimensions
    """        

    
    all_dfs = []

    directory_name = os.path.basename(os.path.normpath(data_directory))
       
    get_type = '*.' + file_type    
    file_list = sorted(glob.glob(os.path.join(data_directory,get_type)))
    file_list.sort()
       
    files = []
    dims = []  
    
    for file in file_list:
        file_name = os.path.basename(file)
        files.append(file_name)
            
        if file_type == 'csv':
            df = pd.read_csv(file, skiprows=1)                       
            dims.append(df.shape)
            data = {'directory' : directory_name,
                    'file' : files,
                    'rows, cols' : dims
            }
            df = pd.DataFrame(data,
                              columns = ['directory', 'file', 'rows, cols'])
        else:
            gz = gzip.open(file, 'rb')
            ds = xr.open_dataset(gz)
            da = ds['tempanomaly']
            dims.append(da.dims) 
            data = {'directory' : directory_name,
                    'file' : files,
                    'dimensions' : dims           
            }    
            df = pd.DataFrame(data,
                              columns = ['directory', 'file', 'dimensions'])
    
    all_dfs.append(df)
        
    catalog_df = pd.concat(all_dfs)   
    return catalog_df

def read_raw_data(file_path, skiprows = 0):
    df = pd.read_csv(file_path, skiprows=skiprows)        
    return df  