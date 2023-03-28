# ECC
Repository for reading the dataset European Cloud Cover (ECC). Available at https://datasets.simula.no/ecc-dataset/. The repositoriy also contains necessary code and examples if you wish to regridd you own cloud cover. 

## Examples 
* Read_ECC.ipynb - Notebook for reading the dataset into a pandas dataframe.
* utils.py - utilities for reading data.
* environment.yml - specifications of package necessary to run the notebooks.
* calc_fractional_cover.py - contains functionality used when regridding data.
* Regridd_NC_GRB_to_ECC.ipynb - Notebook with examples on regridding data originating on both netcdft and grb format. 
* Verifying_regridding.ipynb - Notebook with example verifying that the regridding detected the correct pixels.


## How to get started/Project Enviornment
```bash
git clone https://github.com/simula/european-cloud-cover.git # clone project
conda env create -f environment.yml # create project enviornment 
conda activate ECC # actovate project enviornment
jupyter lab # launch jupyter lab
``` 
## Download the data 
Go to https://datasets.simula.no/ecc-dataset/ and download the dataset as zip-file. Use the following command to create a empty directory at the same level as you cloned ECC. 
```bash
mkdir ECC_DATA
``` 
Extract the data here. The resulting filestructure is as folllow
```bash
├── projectfolder
│   ├── european-cloud-cover
│   │   └── Read_ECC.ipynb
│   │   └── utils.py
│   │   └── README.md
│   │   └── environment.yml
│   │   └── Regridd_NC_GRB_to_ECC.ipynb
│   │   └── calc_fractional_cover.py
|   |   └── Verifying_regridding.ipynb
│   │   └── regridding_info
│   │       └── ERA5_grid_resample_includes_changes_to_indexes_from_30.0_35.0.json
│   │       └── ERA5_grid_resample_includes_changes_to_indexes_from_35.0_40.0.json
│   │       └── ERA5_grid_resample_includes_changes_to_indexes_from_40.0_45.0.json
│   │       └── ERA5_grid_resample_includes_changes_to_indexes_from_45.0_50.0.json
│   │       └── ERA5_grid_resample_includes_changes_to_indexes_from_50.0_55.0.json
│   └── ECC_DATA
│       └── data

```

## Contact
Please contact hannasv@math.uio.no, michael@simula.no, or hugoh@oslomet.no for any questions regarding the dataset.
