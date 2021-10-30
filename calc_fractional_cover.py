import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
save_dir = './regridding_info/'

def area_grid_cell(c_lat, d_lat, d_lon):
        """
        c_lat : float
            Centre point longitude, latitude in degrees

        d_lat, d_lon : float
            delta lat lon in degrees

        Returns : area in km^2

        cdo : If the grid cell area have to be computed it is scaled with the earth radius to square meters.
        """
        R = 6371000  # in M
        # area er egentlig R**2
        area = R*(np.sin((c_lat + d_lat)*np.pi/180) - np.sin((c_lat - d_lat)*np.pi/180) )*(2*d_lon*np.pi/180) # R**2
        return np.abs(area)

def clean_file(satfil):
    """ Remove reduntant categories from eumetsat
    
        Parameteres 
            satfil (str) : filename satelite 
                It accepts both.nc and .grb format
                
        Returns 
            o (3712x3712-array) : satelite data
                Array has two categories, 0-clear, 1-cloudy
    """
    if satfil.split('.')[-1] == 'grb':
        cloudMask = xr.open_dataset(satfil, engine = 'cfgrib')
        o = cloudMask['p260537'].values.reshape( (3712, 3712) )
        o[o>=3.0]=np.nan
        o[o==1.0]=0
        o[o==2.0]=1.0
    else:
        cloudMask = xr.open_dataset(satfil)
        # = np.flipud(cloudMask.cloudMask.values)
        o = cloudMask.cloudMask.values
        #o[o<=2.0]=np.nan
        o[o==1.0]=0
        o[o==2.0]=1.0
        #print(cloudMask)
        # = cloudMask['cloudMask'].values.reshape( (3712, 3712) )
    return o

def area_grid_cell(c_lat, d_lat, d_lon):
    """ Function for computing the area of a 
    
        Parameteres:
            c_lat (float) : coordinate latitde 
            d_lat (float) : extent of pixel in latitudinal direction 
            d_lon (float) : extent of pixel in longitudinal direction
        
        Return:
            area (float) : pixel area
    
    """
    R = 6371000  # in M
    # area er egentlig R**2
    area = R*(np.sin((c_lat + d_lat)*np.pi/180) - np.sin((c_lat - d_lat)*np.pi/180) )*(2*d_lon*np.pi/180) # R**2
    return np.abs(area)


def get_dict_with_all_keys():
    """ Function for merging the coordinate mappings from the entire grid. 
    
        Returns: 
            merged_dict (dict[str]) :dictionary containing coordinate mappings for each degree.
    """
    ex_fil = glob.glob(save_dir + '*ERA5*grid*changes_to_indexes_from*.json')
    merged_dict = {}
    for fil in ex_fil:
        with open(fil, 'r') as f:
            data_grid = json.load(f)
        merged_dict.update(data_grid)
    return merged_dict

def calc_fraction_one_cell(lat = '30.25', lon = '19.25', cmk = None, data = None):
    """ Function for computing the cloud fraction for one cell.
    
        Parameters 
            lat (str(float)) : latitude-cordinate (in ECC-coordninate system)
            lon (str(float)) : longitude-coordinate (in ECC-coordninate system)
            cmk (=None) : array of cloudmasks
            data (=None) : coordinate informations merged dictionary
            
        Returns 
            cloudfraction (float) : areaweighted cloud fraction
            (lat, lon) (str, str): in case of failure the function returns which lat and lon it failed to provide the data for. 
    """

    if data:
        ## Improvements : This should read the files.
        ex = data[lat][lon]
        fraction = 0

        ERA_area = area_grid_cell(float(lat), 0.25/2, 0.25/2)
        SAT_area = 0
        #cmk = np.random.randint(low = 0, high=2, size = len(lat_array))

        for key, item in ex.items():
            index = item['index']
            area  = item['area']

            if len(index) == len(area):
                # , "len index, len are = {}, {}".format(len(index), len(area))
                SAT_area += np.nansum(area)
                #print('nans area')
                #print()
                if np.isnan(np.array(area)).sum() > 0:
                    print('Returns nan for lat {}, lon {}'.format(lat, lon))
                fraction += np.nansum(np.array(area)*np.array(cmk[index]) )
            else:
                print('Returns nan for lat {}, lon {}'.format(lat, lon))
                return np.nan, (lat, lon)
        cloud_fraction = fraction/SAT_area
        return cloud_fraction, None
    else:
        print('Please send data as a attribute.')
        return


def compute(satfil, lats = None, lons = None):
    """ Function for computing the cloudfractions for lists of latitudes and longitudes.
    
    Parameters 
        satfil (str) : filename
        lats List[str]: list of latitude values  
        lons List[str]: list of longitudinal values
        
    Returns
        fractions (pd.DataFrame) : pandas dataframe of the fractions 
        pair (List[Tuple[str, str]
    
    """
    o = clean_file(satfil)
    ex_fil = glob.glob(save_dir + '*ERA5*grid*changes_to_indexes_from*.json')

    clouds = o.reshape(-1)

    _all = {}
    fractions = {}
    pairs=[]

    for fil in ex_fil:
        with open(fil, 'r') as f:
            data_grid = json.load(f)
        _all.update(data_grid)

    for lat in lats:
        fractions[str(lat)] = {}
        for lon in lons:
            a, tup = calc_fraction_one_cell(lat = str(lat),
                                            lon = str(lon),
                                            cmk = clouds,
                                            data = _all)
            if a is np.nan:
                print()
            fractions[str(lat)][str(lon)] = a
            if tup:
                pairs.append(tup)
    import pandas as pd

    return pd.DataFrame.from_dict(fractions), pairs
