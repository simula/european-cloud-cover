import pandas as pd
#import seaborn as sns
import numpy as np
#import matplotlib.pyplot as plt
import glob
from netCDF4 import Dataset
import json
import xarray as xr
#%matplotlib inline

save_dir = './files/'
#coord_dir = '/home/hanna/Desktop/examples_master_thesis/'
nc_files  glob.glob("*.nc")

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

def add(a, b):
    return np.abs(a) + np.abs(b)

def subtract(a, b):
    return np.abs(a) - np.abs(b)

def read_dlon_dlat(save_dir):
    nc_files = glob.glob(save_dir+'*cell*.json')
    with open(nc_files[-1]) as f:
        d =  json.load(f)

    d_phi      = d['dphi']
    d_theta    = d['dtheta']
    cell_areas = d['cell_area']
    lat_array  = d['lat']
    lon_array  = d['lon']
    #save_dict_to_json(d, "changes_lat_lon_cell-area.json", save_dir = save_dir)
    return d_phi, d_theta, cell_areas, lat_array, lon_array


def regrid(lats = None,
           lons = None,
            write_fil = True):

    if lats is None:
        lats = np.arange(30, 56, 0.25)

    if lons is None:
        lons = np.arange(-15, 30, 0.25),

    d_phi, d_theta, cell_areas, lat_array, lon_array = read_dlon_dlat(save_dir)

    c_lat = np.array(lat_array)
    c_lon = np.array(lon_array)
    d_theta = np.array(d_theta)
    d_phi = np.array(d_phi)

    era_step = 0.25

    data = {}
    for lat in lats:
        data[str(lat)] = {}
        for lon in lons:
            data[str(lat)][str(lon)] = {}
            era_AREA = area_grid_cell(lat, era_step/2, era_step/2)
            print("lat = {}, lon = {}".format(lat, lon))
            era_up    = lat + era_step/2
            era_down  = lat - era_step/2
            era_left  = lon - era_step/2
            era_right = lon + era_step/2

            # to ensure correct sign
            cmk_left  = c_lon - np.abs(d_phi)   #- era_right
            cmk_right = c_lon + np.abs(d_phi)   #- era_left
            cmk_up    = c_lat + np.abs(d_theta) #- era_down
            cmk_down  = c_lat - np.abs(d_theta) #- era_up

            data[str(lat)][str(lon)]['centre'] = {}
            data[str(lat)][str(lon)]['down'] = {}
            data[str(lat)][str(lon)]['up'] = {}
            data[str(lat)][str(lon)]['right'] = {}
            data[str(lat)][str(lon)]['left'] = {}
            data[str(lat)][str(lon)]['corner'] = {}

            idx_left_boundary  = np.intersect1d(np.argwhere(cmk_right > era_left),  np.argwhere(cmk_left < era_left) )
            idx_right_boundary = np.intersect1d(np.argwhere(cmk_right > era_right), np.argwhere(cmk_left < era_right) )
            idx_up_boundary    = np.intersect1d(np.argwhere(cmk_up    > era_up),    np.argwhere(cmk_down < era_up) )
            idx_down_boundary  = np.intersect1d(np.argwhere(cmk_up    > era_down),  np.argwhere(cmk_down < era_down) )

            idx_lower_right_corner = np.intersect1d(idx_down_boundary, idx_right_boundary)
            idx_lower_left_corner  = np.intersect1d(idx_down_boundary, idx_left_boundary)
            idx_upper_left_corner  = np.intersect1d(idx_up_boundary,   idx_left_boundary)
            idx_upper_right_corner = np.intersect1d(idx_up_boundary,   idx_right_boundary)

            corner_idx = np.concatenate([idx_lower_right_corner, idx_lower_left_corner,
                                         idx_upper_left_corner, idx_upper_right_corner])

            data[str(lat)][str(lon)]['corner']['index'] = corner_idx.reshape(-1).tolist()

            # TODO add new centre corners. And calculate
            llc_dlat = subtract(cmk_up[idx_lower_left_corner], era_down)/2
            llc_dlon = subtract(era_left, cmk_right[idx_lower_left_corner])/2
            llc_lat  = era_down + llc_dlat
            llc_area = area_grid_cell(llc_lat, llc_dlat, llc_dlon)

            lrc_dlat = subtract(cmk_up[idx_lower_right_corner], era_down)/2
            lrc_dlon = subtract(cmk_left[idx_lower_right_corner], era_right)/2
            lrc_lat  = era_down + lrc_dlat
            lrc_area = area_grid_cell(lrc_lat, lrc_dlat, lrc_dlon)

            ulc_dlat = subtract(era_up, cmk_down[idx_upper_left_corner])/2
            ulc_dlon = subtract(era_left, cmk_right[idx_upper_left_corner])/2
            ulc_lat  = era_up - ulc_dlat

            ulc_area = area_grid_cell(ulc_lat, ulc_dlat, ulc_dlon)

            urc_dlat = subtract(era_up, cmk_down[idx_upper_right_corner])/2
            urc_dlon = subtract(cmk_left[idx_upper_right_corner], era_right)/2
            urc_lat  = era_up - urc_dlat

            urc_area = area_grid_cell(urc_lat, urc_dlat, urc_dlon)

            corner_areas = np.array([lrc_area, llc_area, ulc_area, urc_area])
            data[str(lat)][str(lon)]['corner']['area'] = np.concatenate(corner_areas).reshape(-1).tolist()

            # Removes Corners
            # TODO test if this removes indecies.
            idx_down_boundary = np.array(idx_down_boundary)[np.isin(idx_down_boundary, corner_idx, invert = True)]
            idx_up_boundary = np.array(idx_up_boundary)[np.isin(idx_up_boundary, corner_idx, invert = True)]
            idx_left_boundary = np.array(idx_left_boundary)[np.isin(idx_left_boundary, corner_idx, invert = True)]
            idx_right_boundary = np.array(idx_right_boundary)[np.isin(idx_right_boundary, corner_idx, invert = True)]
            #idx_down_boundary = np.array(idx_down_boundary)[np.isin(idx_down_boundary, corner_idx invert = True)]

            # subsection left boundary OLD
            low_bound = np.argwhere(cmk_down[idx_left_boundary] < era_up  )
            up_bound  = np.argwhere(cmk_up[idx_left_boundary]   > era_down )
            sub_section_left = np.intersect1d(low_bound, up_bound)
            idx_l = np.array(idx_left_boundary)[np.array(sub_section_left)]
            idx_left = idx_l[np.isin(idx_l, corner_idx, invert = True)].tolist()
            data[str(lat)][str(lon)]['left']['index'] = idx_left

            # subsection right boundary
            low_bound = np.argwhere( cmk_down[idx_right_boundary] < era_up )
            up_bound  = np.argwhere( cmk_up[idx_right_boundary] > era_down)
            sub_section_right = np.intersect1d(low_bound, up_bound)

            idx_r = np.array(idx_right_boundary)[np.array(sub_section_right)]
            idx_right = idx_r[np.isin(idx_r, corner_idx, invert = True)].tolist()
            data[str(lat)][str(lon)]['right']['index'] = idx_right

            # Subsection Down Boundary
            one = np.argwhere(cmk_left[idx_down_boundary]  > era_left)
            two = np.argwhere(cmk_right[idx_down_boundary] < era_right)
            sub_section_down = np.intersect1d(one, two)
            idx_d = np.array(idx_down_boundary)[np.array(sub_section_down)]
            idx_down = idx_d[np.isin(idx_d, corner_idx, invert = True)].tolist()
            data[str(lat)][str(lon)]['down']['index'] =  idx_down
            #sub_section_down.reshape(-1).tolist()

            # subsection up boundary
            one = np.argwhere( cmk_left[idx_up_boundary]  > era_left)
            two = np.argwhere( cmk_right[idx_up_boundary] < era_right)
            sub_section_up = np.intersect1d(one, two)
            print(sub_section_up)
            idx_u = np.array(idx_up_boundary)[np.array(sub_section_up)]
            idx_up = idx_u[np.isin(idx_u, corner_idx, invert = True)].tolist()
            data[str(lat)][str(lon)]['up']['index'] = idx_up

            # test that these are empty
            t1 = np.intersect1d(idx_d, idx_u)
            t2 = np.intersect1d(idx_r, idx_l)
            # assert len(t1) == len(t2) == 0, "intercept up down  {}, intersect left right {}.".format(t1, t2)

            if len(t1) != 0:
                print("\n Problem up, down lat {} lon {}. \n".format(lat, lon))

            if len(t2) != 0:
                print("\n Problem left, right lat {} lon {}. \n".format(lat, lon))
            # Calculate Boundaries

            # AREA left boundary
            dlon_lf = subtract(cmk_right[idx_left], era_left)/2
            dlat_lf = d_theta[idx_left]
            lat_lf  = c_lat[idx_left]
            left_areas = area_grid_cell(lat_lf, dlat_lf, np.abs(dlon_lf))
            data[str(lat)][str(lon)]['left']['area'] = left_areas.reshape(-1).tolist()

            # AREA right boundary -- her er problemet !!!!!!!!
            dlon_rb = subtract(era_right, cmk_left[idx_right])/2
            dlat_rb = d_theta[idx_right]
            lat_rb  = c_lat[idx_right]
            right_area = area_grid_cell(lat_rb, dlat_rb, np.abs(dlon_rb))
            data[str(lat)][str(lon)]['right']['area'] = right_area.ravel().tolist()

            # AREA down boundary
            dlat_down = subtract(era_down, cmk_up[idx_down])/2
            lat_down = era_down + dlat_down
            dlon_down = d_phi[idx_down]
            down_area = area_grid_cell(lat_down, dlat_down, dlon_down)
            data[str(lat)][str(lon)]['down']['area'] = down_area.reshape(-1).tolist()

            # AREA up
            dlat_up = subtract(era_up, cmk_down[idx_up])/2
            lat_up = era_up - dlat_up
            #lon_up = c_lon[idx_up_boundary][sub_section_up]
            dlon_up = d_phi[idx_up]
            up_area = area_grid_cell(lat_up, dlat_up, np.abs(dlon_up))
            data[str(lat)][str(lon)]['up']['area'] = up_area.reshape(-1).tolist()
            # = np.sum(up_area)

            # Index centres. Can safly assume centre cells are correct.
            idx_centre_one = np.intersect1d(np.argwhere(cmk_left  > era_left),
                                            np.argwhere(cmk_right < era_right))


            idx_centre_two = np.intersect1d(np.argwhere(cmk_up   < era_up),
                                            np.argwhere(cmk_down >  era_down))

            idx_centre_cells = np.intersect1d( idx_centre_one, idx_centre_two )
            data[str(lat)][str(lon)]['centre']['index'] = idx_centre_cells.ravel().tolist()

            lat_centre_cells = c_lat[idx_centre_cells]
            dlat_centre      = d_theta[idx_centre_cells]
            dlon_centre      = d_phi[idx_centre_cells]

            centre_area      = area_grid_cell(lat_centre_cells, dlat_centre, dlon_centre)

            data[str(lat)][str(lon)]['centre']['area'] = centre_area.reshape(-1).tolist()

        if lat%5==0 and lat > 30 and write:
            print("Saves file every lat {} lon {}.".format(lat, lon))
            filnavn = 'ERA5_grid_resample_test_right_boundary_{}_{}.json'.format(float(lat), lon)
            with open(save_dir + filnavn, 'w') as f:
                json.dump(data, f)
                data = {}
        return data
        
if __name__ == '__main__':
    regrid()
