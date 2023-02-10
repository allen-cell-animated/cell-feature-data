const fsPromises = require("fs").promises;
const Ajv = require("ajv").default;

const { DATA_FOLDER_NAME } = require("../src/process-single-dataset/constants");
const {
  readDatasetJson
} = require("../src/utils");
const dataPrep = require("../src/data-validation/data-prep");
const unpackInputDataset = require("../src/process-single-dataset/steps/unpack-input-dataset")

// referenced partial schemas
const refSchemas = [
  require("../src/data-validation/schema/definitions.schema.json"),
  require("../src/data-validation/schema/discrete-feature-options.schema.json"),
  require("../src/data-validation/schema/array-items/discrete-feature-option.schema.json"),
  require("../src/data-validation/schema/array-items/file-info.schema.json"),
  require("../src/data-validation/schema/array-items/input-measured-features.schema.json"),
];

// Schemas that describe the handoff files that define a dataset or a
// collection of datasets.
const inputMegaset = require("../src/data-validation/schema/input-megaset.schema.json");
const inputDatasetInfo = require("../src/data-validation/schema/input-dataset-info.schema.json");
const inputMeasuredFeatures = require("../src/data-validation/schema/input-measured-features-doc.schema.json");
const inputDataSet = require("../src/data-validation/schema/input-dataset.schema.json");
const inputImages = require("../src/data-validation/schema/images.schema.json");
const featureDef = require("../src/data-validation/schema/feature-def.schema.json");

const INPUT_DATASET_SCHEMA = [
  ...refSchemas,
  inputImages,
  featureDef,
  inputMegaset,
  inputDatasetInfo,
  inputMeasuredFeatures,
  inputDataSet,
];
const INPUT_DATASET_SCHEMA_FILE = "input-dataset.schema.json";
const INPUT_MEGASET_SCHEMA_FILE = "input-megaset.schema.json";

const ajv = new Ajv({
  coerceTypes: true,
  removeAdditional: true,
  schemas: INPUT_DATASET_SCHEMA,
});

const checkForError = (fileName, json, schemaFileName) => {
  const { valid, error } = dataPrep.validate(
    json,
    ajv.getSchema(schemaFileName)
  );
  if (!valid) {
    console.log(
      "\x1b[0m",
      `${fileName}`,
      "\x1b[31m",
      `failed because: ${JSON.stringify(error)}`,
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


const validateDatasets = () => {
  fsPromises
    .readdir(`./${DATA_FOLDER_NAME}`)
    .then(async (files) => {
      const foldersToCheck = [];
      let hasError = false;
      const checkSingleDatasetInput = async (datasetFolder) => {
        const inputDataset = await unpackInputDataset(datasetFolder);
        const foundError = checkForError(
          `${datasetFolder}`,
          inputDataset,
          INPUT_DATASET_SCHEMA_FILE
        );
        if (foundError) {
          hasError = true;
        }
      };

      for (const name of files) {
        try {
          const subFiles = await fsPromises.readdir(`./${DATA_FOLDER_NAME}/${name}`);
          if (subFiles.includes("dataset.json")) {
            foldersToCheck.push(`./${DATA_FOLDER_NAME}/${name}`);
          }
        } catch (error) {console.log(error)}
      }
      for (const datasetFolder of foldersToCheck) {
        const topLevelJson = await readDatasetJson(datasetFolder);
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
            await checkSingleDatasetInput(datasetReadFolder);
          }
        } else {
          await checkSingleDatasetInput(datasetFolder);
        }
      }
      return hasError;
    })
    .then((hasError) => {
      if (hasError) {
        console.log("\x1b[31m");
        throw Error("Validation failed");
      }
    }).catch(console.log)
};

validateDatasets();
