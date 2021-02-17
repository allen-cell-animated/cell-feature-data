const fsPromises = require('fs').promises;

const uploadDatasetAndManifest = require("./upload-dataset-and-manifest");
const uploadFeatureDefs = require("./upload-feature-defs");
const uploadCellLines = require("./upload-cell-lines");
const formatAndWritePerCellJsons = require("./write-per-cell-jsons");
const uploadFileInfo = require("./upload-file-info");

const FirebaseHandler = require('../scripts/firebase-handler');

const args = process.argv.slice(2);
console.log('myArgs: ', args);

const datasetReadFolder = args[0];


const readDatasetInfo = async () => {
    const data = await fsPromises.readFile(`${datasetReadFolder}/dataset.json`)
    return JSON.parse(data)
}

const processDataset = async () => {

    if (!datasetReadFolder) {
        console.log("NEED A DATASET FOLDER TO PROCESS")
        process.exit(1)
    }
    
    fsPromises.readdir(datasetReadFolder)
        .catch ((error) => {
            console.log("COULDN'T READ DIRECTORY:", error)
        })
    
    const datasetJson = await readDatasetInfo()
    const {
        id
    } = datasetJson;
    console.log(id)
    const firebaseHandler = new FirebaseHandler(id);

    // 1. upload dataset description and manifest
    // await uploadDatasetAndManifest(firebaseHandler, datasetJson, datasetReadFolder)
    // 2. check dataset feature defs for new features, upload them if needed
    // await uploadFeatureDefs(firebaseHandler, datasetReadFolder)
    // 3. upload cell lines TODO: add check if cell line is already there
    // await uploadCellLines(firebaseHandler, datasetReadFolder)
    // 4. format file info, write to json locally
    await formatAndWritePerCellJsons(datasetReadFolder, "./data")
    // 5. upload file info per cell
    // await uploadFileInfo(firebaseHandler, "./data")
    process.exit(0)
}    

processDataset()
