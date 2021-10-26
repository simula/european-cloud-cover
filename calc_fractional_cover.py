import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

def read_dlon_dlat(save_dir):
    nc_files = glob.glob(save_dir+'*cell*.json')
    #print(nc_files)
    with open(nc_files[-1]) as f:
        d =  json.load(f)

    d_phi      = d['dphi']
    d_theta    = d['dtheta']
    cell_areas = d['cell_area']
    lat_array  = d['lat']
    lon_array  = d['lon']
    return d_phi, d_theta, cell_areas, lat_array, lon_array

def clean_file(satfil):
    if satfil.split('.')[-1] == 'grb':
        print("detect grib file")
        cloudMask = xr.open_dataset(satfil, engine = 'cfgrib')
        o = cloudMask['p260537'].values.reshape( (3712, 3712) )
        o[o>=3.0]=np.nan
        o[o==1.0]=0
        o[o==2.0]=1.0
    else:
        print(" Detect nc file - this is already rewritten to binary.")
        cloudMask = xr.open_dataset(satfil)
        #print(cloudMask)
        o = cloudMask['cloudMask'].values.reshape( (3712, 3712) )

    #import seaborn as sns
    #sns.heatmap(o)
    #plt.show()

    return o

def area_grid_cell(c_lat, d_lat, d_lon):
        R = 6371000  # in M
        # area er egentlig R**2
        area = R*(np.sin((c_lat + d_lat)*np.pi/180) - np.sin((c_lat - d_lat)*np.pi/180) )*(2*d_lon*np.pi/180) # R**2
        return np.abs(area)


def get_dict_with_all_keys():
    ex_fil = glob.glob(save_dir + '*ERA5*grid*changes_to_indexes_from*.json')
    merged_dict = {}
    for fil in ex_fil:
        with open(fil, 'r') as f:
            data_grid = json.load(f)
        merged_dict.update(data_grid)
    return merged_dict

def calc_fraction_one_cell(lat = '30.25', lon = '19.25', cmk = None, data = None):

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

        return fraction/SAT_area*ERA_area, None
    else:
        print('Please send data as a attribute.')
        return


def compute(satfil, lats = None, lons = None):
    o = clean_file(satfil)
    d_phi, d_theta, cell_areas, lat_array, lon_array = read_dlon_dlat(save_dir)
    ex_fil = glob.glob(save_dir + '*ERA5*grid*changes_to_indexes_from*.json')

    clouds = o.reshape(-1)

    _all = {}
    fractions = {}

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

    return pd.DataFrame.from_dict(fractions), pair
