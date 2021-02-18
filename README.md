# To process a dataset:

## Setup
### Expected files in a dataset:
- `dataset.json`: a json file with metadata about the dataset and the names of the other files
- featureDefs: a json describing the measured features in this dataset
- featuresData: a json listing the per cell data
- cellLineData: a json of the cell line definitions

### Needed in .env file:
```
NODE_ENV="production"
# used if NODE_ENV === "production"
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_DB_URL=
FIREBASE_ID=
STORAGE_BUCKET=
MESSAGING_SENDER_ID=
FIREBASE_TOKEN=
FIREBASE_EMAIL=

# used if NODE_ENV !== "production"
TESTING_FIREBASE_API_KEY=
TESTING_FIREBASE_AUTH_DOMAIN=
TESTING_FIREBASE_DB_URL=
TESTING_FIREBASE_ID=
TESTING_STORAGE_BUCKET=
TESTING_MESSAGING_SENDER_ID=
TESTING_FIREBASE_TOKEN=
TESTING_FIREBASE_EMAIL=

AWS_SECRET=
AWS_ID=
```
## To run process:
`node process-dataset [PATH/TO/DATASET]`