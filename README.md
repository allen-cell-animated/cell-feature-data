[![Dataset validation](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/validate.yml)

# For dataset creators:
## To create a new dataset:
#### Option 1: Upload a csv file and use the `create-dataset` python script
1. make a branch or fork of this repo
2. navigate to `dataset-processor-python` and create the virtual environment if not already created, run `python3 -m venv [ENV-NAME]`
3. activate the virtual environment: `source [ENV-NAME]/bin/activate`
4. install the required packages: `pip install -r requirements.txt`
5. run the `create-dataset` script with the path to your csv file
    - `npm run create-dataset [PATH/TO/CSV]`
    - This will create a new dataset folder under `data` with the same name as the csv file
    - This will process the csv file and create the necessary json files for the dataset
    - This will ask for additional information about the dataset by prompting in the terminal, and then update the json files based on the input
6. deactivate the virtual environment once finished using: `deactivate`

#### Option 2: Manually create json files within a dataset folder
1. make a branch or fork of this repo
2. create a new dataset folder under `data`
    #### Expected files in a dataset directory:
    - `dataset.json`: a json file with metadata about the dataset and the names of the other files. *this is the only filename that matters. Otherwise everything is a relative path.*
    - a json file describing the measured features in this dataset. Key in `dataset.json`: `featureDefsPath`
    - a json file listing the per cell data. Key in `dataset.json`: `featuresDataPath`
    - a json file with settings for volume data channels in the 3d viewer. Key in `dataset.json`: `viewerSettingsPath`

#### After creating the dataset:
  
1. Before pushing a PR back to this repo, run the preliminary data consistency checks locally and make sure the validation passes. If it doesn't check the logs to see what went wrong and fix any errors.
    * to validate a single dataset: `npm run validate-single-dataset [PATH/TO/DATASET]` 
    * to validate all datasets: `npm run validate-datasets`

2. If everything looks good, run the [process dataset from `Actions`](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/upload-dataset.yml) by clicking the "Run workflow" dropdown and entering the following settings:
    * set `branch` to your branch
    * enter the folder name that contains your dataset
    * leave checkbox unchecked if this is your first time uploading
    * leave db set to `staging`

#### For more on what these files should look like, look at `process-dataset/data-validation/schema.js` and [Full spec documentation](https://allen-cell-animated.github.io/cell-feature-data/HandoffSpecification.html)

## To view your dataset:
#### Option 1: Point cell feature explorer staging site to staging database
1. Go to [Manual deploy Action](https://github.com/allen-cell-animated/cell-feature-explorer/actions/workflows/manual-deploy.yml) 
    * Click the workflow drop down, leave branch at `main`
    * Set `Deploy with staging db` to `true`
2. Go to `staging.cfe.allencell.org`

#### Option 2: Run Cell Feature explorer locally
1. `git clone https://github.com/allen-cell-animated/cell-feature-explorer.git`
2. `npm i`
2. `npm run start:dev-db`




# For Developers: 
Clone or fork this repo
run `npm i`

## Setup
### A glance of cloud firestore  
- [documentation + tutorial](https://firebase.google.com/docs/firestore) 
- [get started](https://firebase.google.com/docs/firestore/quickstart)
  
### Set up a dev database
- choose Test mode in your security rules 
- add your required secret tokens to .env file 
- set NODE_ENV="dev" in .env file
> Please refer to the `Needed in .env file` section for obtaining tokens  

### Needed in .env file:
```
NODE_ENV= "production" || "staging" || "dev"
AWS_SECRET=
AWS_ID=

# used if NODE_ENV === "production"
FIREBASE_TOKEN=
FIREBASE_EMAIL=

# used if NODE_ENV === "staging"
STAGING_FIREBASE_TOKEN= 
STAGING_FIREBASE_EMAIL=

# used if NODE_ENV === "dev"
DEV_FIREBASE_TOKEN= project settings/service accounts/generate new private key
DEV_FIREBASE_ID= project settings/general/project ID
DEV_FIREBASE_EMAIL= project settings/services accounts/firebase service account 
```
> To access `AWS`, `production`, or `staging`, please contact the development team for the necessary credentials 

### Three database endpoints:
- `dev`: developer's personal testing database, the default option for development. Create your own credentials to access. 
- `staging`: group testing || for scientists to review. NODE_ENV=="staging"
- `production`: production database for cfe.allencell.org. NODE_ENV=="production"

## To process a new dataset:

`node process-dataset [PATH/TO/DATASET]`
or
`npm run process-dataset [PATH/TO/DATASET]`

To skip the fileInfo upload but run all the other steps (fileInfo upload takes a long time because firebase limits to 500 uploads per request):

`node process-dataset [PATH/TO/DATASET] true`
or 
`npm run process-dataset [PATH/TO/DATASET] true`

## Upload a dataset card image after the data has been uploaded
`npm run upload-image [PATH/TO/DATASET]`

## Release dataset to production
`npm run release-dataset [MEGASET_NAME]` // will release every dataset in a megaset. Note, this isn't the folder name, it's the megaset name
`npm run release-dataset [DATASET_ID]` // will release a dataset that isn't part of a megaset, id should be in the format `[NAME]_v[VERSION]`
`npm run release-dataset [MEGASET_NAME]  [DATASET_ID]` // will a dataset contained within a megaset, id should be in the format `[NAME]_v[VERSION]` 

