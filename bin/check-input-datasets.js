const fsPromises = require("fs").promises;
const { DATA_FOLDER_NAME } = require("../src/process-single-dataset/constants");
const {validateSingleDataset} = require("./check-single-dataset");


const validateDatasets = () => {
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
        hasError = await validateSingleDataset(datasetFolder);
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


  validateDatasets();
