const fsPromises = require("fs").promises;
const {
  getInputDatasetSchema,
} = require("../src/data-validation/get-input-dataset-schema");
const { DATA_FOLDER_NAME } = require("../src/process-single-dataset/constants");
const utils = require("../src/utils");
const dataPrep = require("../src/data-validation/data-prep");
const unpackInputDataset = require("../src/data-validation/unpack-input-dataset");
// referenced partial schemas
const INPUT_DATASET_SCHEMA_FILE = "input-dataset.schema.json";
const INPUT_MEGASET_SCHEMA_FILE = "input-megaset.schema.json";
const ajv = getInputDatasetSchema();

const checkForError = (fileName, json, schemaFileName) => {
  const { valid, error } = dataPrep.validate(
    json,
    ajv.getSchema(schemaFileName)
  );
  let datasetsError = false;
  let ErrorMsg = "";
  if (json["feature-defs"]) {
    const featuresDataOrder = json.dataset.featuresDataOrder;
    const featureDefsData = json["feature-defs"];
    const result = utils.validateFeatureDataKeys(
      featuresDataOrder,
      featureDefsData
    );
    if (result.featureKeysError) {
      datasetsError = result.featureKeysError;
      ErrorMsg = result.keysErrorMsg;
    }
  }
  if (json["dataset"]) {
    const totalCells = json.dataset.userData.totalCells;
    const totalFOVs = json.dataset.userData.totalFOVs;
    const result = utils.validateUserDataValues(totalCells, totalFOVs);
    if (result.userDataError) {
      datasetsError = result.userDataError;
      ErrorMsg = result.userDataErrorMsg;
    }
  }

  if (!valid || datasetsError) {
    console.log(
      "\x1b[0m",
      `${fileName}`,
      "\x1b[31m",
      `failed because: ${JSON.stringify(error || ErrorMsg)}`,
      "\x1b[0m"
    );
    return true;
  } else {
    console.log(
      "\x1b[0m",
      `${fileName}: check against ${schemaFileName}`,
      "\x1b[32m",
      "passed",
      "\x1b[0m"
    );
    return false;
  }
};

const checkSingleDatasetInput = async (datasetFolder) => {
  const inputDataset = await unpackInputDataset(datasetFolder);
  const foundError = checkForError(
    `${datasetFolder}`,
    inputDataset,
    INPUT_DATASET_SCHEMA_FILE
  );
  return foundError;
};

// const validateSingleDataset = async (datasetFolder) => {
//   console.log(`Checking 1 ${datasetFolder}`);
//   const topLevelJson = await utils.readDatasetJson(datasetFolder);
//   if (topLevelJson.datasets) {
//     // is a megaset, need to check both megaset
//     // file and each dataset folder
//     const foundError = checkForError(
//       `${datasetFolder}/dataset.json`,
//       topLevelJson,
//       INPUT_MEGASET_SCHEMA_FILE
//     );
//     if (foundError) {
//       return true;
//     }
//     for (const subDatasetFolder of topLevelJson.datasets) {
//       const datasetReadFolder = `${datasetFolder}/${subDatasetFolder}`;
//       const subError = await checkSingleDatasetInput(datasetReadFolder);
//       if (subError) {
//         return true;
//       }
//     }
//   } else {
//     const singleDatasetError = await checkSingleDatasetInput(datasetFolder);
//     if (singleDatasetError) {
//       return true;
//     }
//   }
//   return false;
// };

// if (process.argv[2]) {
//   const datasetFolder = process.argv[2];
//   validateSingleDataset(datasetFolder);
// }

const datasetCheck =() => {
  return "feature logs"
}

// const datasetCheck =() => {
  // const args = process.argv.slice(2);
  // const inputFolder = args[0];
// datasetData = dataset.json file contents
// measuredFeatures = cell-feature-analysis file contents
// dataOrder = datasetData.featuresDataOrder
// testCaseFeatures = measuredFeatures[0].features
// toLog = {}
// for each featureName, index in testCaseFeatures:
//   toLog[featureName] = testCaseFeatures[index]
// log out 
// console.log("here is the current data order for the first cell:
      // JSON.stringify(toLog)
      
      // if that looks incorrect, please address in dataset.json, featuresDataOrder"


module.exports = {
  checkForError,
  checkSingleDatasetInput,
  datasetCheck
};
