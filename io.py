""" Collection of helper function used to read the European Cloud Cover dataset.
"""

import os, sys
import glob

import numpy as np
import xarray as xr

def read_dataset_to_dataframe(path_input, start = '2012-01-01',
            stop = '2012-01-31', include_start = True, include_stop = True):
    """
    Parameteres
    ----------------------
    start : str
        Start of period. First day included. (default '2012-01-01')
    stop : str, optional
        end of period. Last day included. (default '2012-01-31')

    Returns
    -----------
    df : pd.DataFrame
        Data in DataFrame
    """
    df = None
    dataset = get_xarray_dataset_for_period(path_input=path_input, start = start, stop = stop, include_start = include_start, include_stop = include_stop)
    df =  dataset.to_dataset()
    return df

def merge(files):
    """ Merging a list of filenames into a dataset.open_mfdataset

    Parameteres
    -----------
    files : List[str]
        List of abolute paths to files.
    Returns
    ------------
     _ : xr.dataset
        Merged files into one dataset.
    """
    assert len(files) != 0, 'No files to merge'
    return xr.open_mfdataset(files, compat='no_conflicts')

def get_xarray_dataset_for_period(path_input, start = '2012-01-01',
        stop = '2012-01-31', include_start = True, include_stop = True):
    """ Reads data from the requested period into a xarray dataset.
    I stop is not provided it defaults to one month of data.

    Parameteres
    ----------------------
    start : str
        Start of period. First day included. (default '2012-01-01')
    stop : str, optional
        end of period. Last day included. (default '2012-01-31')
    Returns
    -----------------------
    data : xr.Dataset
        Dataset including all variables in the requested period.
    """
    #from utils import merge
    files = get_list_of_files(path_input=path_input, start = start, stop = stop,
            include_start = include_start, include_stop = include_stop)

    print("Mergingn {}  ... This may take a while.".format(len(files)))
    data = merge(files)
    if stop is not None:
        data = data.sel(time = slice(start, stop))
    return data

def get_list_of_files(path_input, start = '2012-01-01', stop = '2012-01-31',
        include_start = True, include_stop = True):
    """ Returns list of files containing data for the requested period.
    Parameteres
    ----------------------
    path_input : None
        sets path to input
    start : str
        Start of period. First day included. (default '2012-01-01')
    stop : str
        end of period. Last day included. (default '2012-01-31')
    include_start : bool (True)
        Bool to decide whether to include the start time in the list of files. 
    include_stop : bool (True)
        Bool to decide whether to include the stop time in the list of files.

    Returns
    -----------------------
    subset : List[str]
        List of strings containing all the absolute paths of files containing
        data in the requested period.
    """

    # Remove date.
    parts = start.split('-')
    start_search_str = '{}_{:02d}'.format(parts[0], int(parts[1]))

    if stop is not None:
        parts = stop.split('-')
        stop_search_str = '{}_{:02d}'.format(parts[0], int(parts[1]))
    else:
        stop_search_str = ''

    print('\n Searching in directory {} \n'.format( path_input))

    if (start_search_str == stop_search_str) or (stop is None):
        subset = glob.glob(os.path.join( path_input, '{}*.nc'.format(start_search_str)))
    else:
        # get all files
        files = glob.glob(os.path.join( path_input, '*.nc' ))
        files = np.sort(files) # sorting then for no particular reson

        if include_start and include_stop:
            min_fil = os.path.join(path_input, start_search_str + '_q.nc')
            max_fil = os.path.join(path_input, stop_search_str + '_tcc.nc')

            smaller = files[files <= max_fil]
            subset  = smaller[smaller >= min_fil] # results in all the files

        elif include_start and not include_stop:
            min_fil = os.path.join(path_input, start_search_str + '_q.nc')
            max_fil = os.path.join(path_input, stop_search_str + '_q.nc')

            smaller = files[files < max_fil]
            subset  = smaller[smaller >= min_fil] # results in all the files

        elif not include_start and include_stop:
            min_fil = os.path.join(path_input, start_search_str + '_tcc.nc')
            #print('detected min fil {}'.format(min_fil))
            max_fil = os.path.join(path_input, stop_search_str + '_tcc.nc')

            smaller = files[files <= max_fil]
            subset  = smaller[smaller > min_fil] # results in all the files
        else:
            raise ValueError('Something wierd happend. ')
    return subset
