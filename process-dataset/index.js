const fsPromises = require('fs').promises;

const uploadDatasetAndManifest = require("./steps/upload-dataset-and-manifest");
const uploadFeatureDefs = require("./steps/upload-feature-defs");
const uploadCellLines = require("./steps/upload-cell-lines");
const formatAndWritePerCellJsons = require("./steps/write-per-cell-jsons");
const uploadCellCountsPerCellLine = require("./steps/upload-cell-counts");
const uploadFileInfo = require("./steps/upload-file-info");
const uploadFileToS3 = require("./steps/upload-to-aws");

const FirebaseHandler = require('./firebase/firebase-handler');

const TEMP_FOLDER = "./data";
const args = process.argv.slice(2);
console.log('Received: ', args);

const datasetReadFolder = args[0];
const skipFileInfoUpload = args[1];

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
    console.log("Dataset id:", id)
    const firebaseHandler = new FirebaseHandler(id);
    const fileNames = {
        featureDefs: datasetJson.featureDefs,
        featuresData: datasetJson.featuresData,
        cellLineData: datasetJson.cellLineData,
    }
    for (const key in fileNames) {
        if (Object.hasOwnProperty.call(fileNames, key)) {
            if (!fileNames[key]) {
                console.error("Missing file name:", key);
                process.exit(1);
            }
        }
    }

    // 1. upload dataset description and manifest
    const manifestRef = await uploadDatasetAndManifest(firebaseHandler, datasetJson, datasetReadFolder, fileNames.featureDefs);
    // 2. check dataset feature defs for new features, upload them if needed
    await uploadFeatureDefs(firebaseHandler, datasetReadFolder, fileNames.featureDefs);
    // 3. upload cell lines TODO: add check if cell line is already there
    const formattedCellLines = await uploadCellLines(firebaseHandler, datasetReadFolder, fileNames.cellLineData);
    // 4. format file info, write to json locally
    await formatAndWritePerCellJsons(datasetReadFolder, TEMP_FOLDER, fileNames.featuresData, formattedCellLines);
    // 5. upload file info per cell
    const fileInfoLocation = await uploadFileInfo(firebaseHandler, TEMP_FOLDER, skipFileInfoUpload === "true");
    // 6. upload cell line subtotals
    await uploadCellCountsPerCellLine(TEMP_FOLDER, firebaseHandler);
    // 7. upload json to aws
    const awsLocation = await uploadFileToS3(id, TEMP_FOLDER);
    // 8. update dataset manifest with location for data
    const updateToManifest = {
        ...fileInfoLocation, 
        ...awsLocation
    }
    console.log("updating manifest", updateToManifest)
    await firebaseHandler.updateDatasetDoc(manifestRef)
    await firebaseHandler.updateManifest(updateToManifest)
    process.exit(0)
}    

processDataset()
