# ECC
Repository for reading the dataset European Cloud Cover (ECC). Available at https://datasets.simula.no/ecc-dataset/.

## Examples 
* Read_ECC.ipynb - Notebook for reading the dataset into a pandas dataframe.
* utils.py - utilities for reading data.
* environment.yml - specifications of package necessary to run the notebooks.


## How to get started/Project Enviornment
```bash
git clone https://github.com/hannasv/ECC.git # clone project
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
│   ├── ECC
│   │   └── Read_ECC.ipynb
│   │   └── utils.py
│   │   └── README.md
│   │   └── environment.yml
│   └── ECC_DATA
│       └── data

```

## Contact
Please contact hannasv@math.uio.no, michael@simula.no, or hugoh@oslomet.no for any questions regarding the dataset.
