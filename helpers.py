""" Properties of the ECC dataset.
"""

LAT = (30,50)
LON = (-15,25)
SPATIAL_RESOLUTION = 0.25
TEMPORAL_RESOLUTION = 'h' # TODO: this need to be a proper dt format

EXTENT = [LAT, LON]
VARIABLES =  ["t2m", 'sp', 'q', 'r', 'tcc']

LONGNAME = {"t2m":"Temperature", 'q':"Specific Humidity",
            'sp':"Surface Pressure", 'r': "Relative Humidity",
            'tcc':"Cloud Fractional Cover"}

UNITS = {"t2m":"K", 'sp':"Pa", 'q':"kg kg^-1", 'r': "1", 'tcc':"1"}
