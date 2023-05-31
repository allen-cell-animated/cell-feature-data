const fsPromises = require("fs").promises;
const path = require("path");
const {
  getInputDatasetSchema,
} = require("../src/data-validation/get-input-dataset-schema");
const { DATA_FOLDER_NAME } = require("../src/process-single-dataset/constants");
const utils = require("../src/utils");
const dataPrep = require("../src/data-validation/data-prep");
const unpackInputDataset = require("../src/data-validation/unpack-input-dataset");
const {checkForError, checkSingleDatasetInput, datasetCheck} = require("./check-single-dataset");
// referenced partial schemas
const INPUT_DATASET_SCHEMA_FILE = "input-dataset.schema.json";
const INPUT_MEGASET_SCHEMA_FILE = "input-megaset.schema.json";
const ajv = getInputDatasetSchema();


const validateDatasets = (singleDatasetFolder = null) => {
  fsPromises
    .readdir(`./${DATA_FOLDER_NAME}`)
    .then(async (files) => {
      const foldersToCheck = [];
      let hasError = false;
      for (const name of files) {
        try {
          const subFiles = await fsPromises.readdir(
            `./${DATA_FOLDER_NAME}/${name}`
          );
          if (subFiles.includes("dataset.json")) {
            foldersToCheck.push(`./${DATA_FOLDER_NAME}/${name}`);
          }
        } catch (error) {
          console.log(error);
        }
      }
      for (const datasetFolder of foldersToCheck) {
        // skip this dataset if singleDatasetFolder is specified
        if (singleDatasetFolder && path.basename(datasetFolder) !== path.basename(singleDatasetFolder)) { 
          continue; 
        } else if (singleDatasetFolder) {
          console.log(`logging featureName and order... ${datasetFolder}`);
          datasetCheck();
        }; 
        const topLevelJson = await utils.readDatasetJson(datasetFolder);
        if (topLevelJson.datasets) {
          // is a megaset, need to check both megaset
          // file and each dataset folder
          const foundError = checkForError(
            `${datasetFolder}/dataset.json`,
            topLevelJson,
            INPUT_MEGASET_SCHEMA_FILE
          );
          if (foundError) {
            hasError = true;
          }
          for (const subDatasetFolder of topLevelJson.datasets) {
            const datasetReadFolder = `${datasetFolder}/${subDatasetFolder}`;
            if (singleDatasetFolder) {
              console.log(`logging featureName and order... ${datasetFolder}`);
              datasetCheck();
            };
            const foundSubError = await checkSingleDatasetInput(datasetReadFolder);
            if (foundSubError) {
              hasError = true;
            }
          }
        } else {
          const foundError = await checkSingleDatasetInput(datasetFolder);
          if (foundError) {
            hasError = true;
          }
        }
      }
      return hasError;
    })
    .then((hasError) => {
      if (hasError) {
        console.log("\x1b[31m");
        throw Error("Validation failed");
      }
    });
};

if (process.argv[2]) {
  validateDatasets(process.argv[2]);
} else {
  validateDatasets();
}
