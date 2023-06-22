const {
  getInputDatasetSchema,
} = require("../src/data-validation/get-input-dataset-schema");
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
  let errorMsg = "";
  if (json["feature-defs"]) {
    const featuresDataOrder = json.dataset.featuresDataOrder;
    const featureDefsData = json["feature-defs"];
    const result = utils.validateFeatureDataKeys(
      featuresDataOrder,
      featureDefsData
    );
    if (result.featureKeysError) {
      datasetsError = result.featureKeysError;
      errorMsg = result.keysErrorMsg;
    }
  }
  if (json["dataset"]) {
    const totalCells = json.dataset.userData.totalCells;
    const totalFOVs = json.dataset.userData.totalFOVs;
    const result = utils.validateUserDataValues(totalCells, totalFOVs);
    if (result.userDataError) {
      datasetsError = result.userDataError;
      errorMsg = result.userDataErrorMsg;
    }
  }

  if (!valid || datasetsError) {
    console.log(
      "\x1b[0m",
      `${fileName}`,
      "\x1b[31m",
      `failed because: ${JSON.stringify(error || errorMsg)}`,
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
  if (foundError) {
    return true;
  };
};

const datasetFeatureMap = async (datasetFolder) => {
  const inputDataset = await unpackInputDataset(datasetFolder);
  const dataOrder = inputDataset.dataset.featuresDataOrder;
  const testCaseFeatures = inputDataset["measured-features"][0].features;
  const toLog = {};
  for (let i = 0; i < testCaseFeatures.length; i++) {
    toLog[dataOrder[i]] = testCaseFeatures[i];
  }
  console.log(
    "The current features data order for the first image in",
    "\x1b[34m",
    `${datasetFolder}:`,
    "\x1b[33m",
    JSON.stringify(toLog, null, 2),
    "\x1b[0m"
  );

  console.log(
    "\x1b[30m", 
    "If the data looks incorrect, please update featuresDataOrder in dataset.json",
    "\x1b[0m" 
  );
};


const validateSingleDataset = async (datasetFolder, mapFeatures=false) => {
  const topLevelJson = await utils.readDatasetJson(datasetFolder);
  let hasError = false;
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
      const foundSubError = await checkSingleDatasetInput(datasetReadFolder);
      if (foundSubError) {
        hasError = true;
      }
      if (mapFeatures) {
        datasetFeatureMap(datasetReadFolder);
      }
    }
  } else {
    const foundError = await checkSingleDatasetInput(datasetFolder);
    if (foundError) {
      hasError = true;
    }
    if (mapFeatures) {
      datasetFeatureMap(datasetFolder);
    }
  }
  return hasError;
};

if (process.argv[2]) {
  const datasetFolder = process.argv[2];
  validateSingleDataset(datasetFolder, true);
}


module.exports = {
  validateSingleDataset
};