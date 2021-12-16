const fsPromises = require('fs').promises;

const uploadDatasetAndManifest = require("./steps/upload-dataset-and-manifest");
const uploadFeatureDefs = require("./steps/upload-feature-defs");
const formatAndWritePerCellJsons = require("./steps/write-per-cell-jsons");
const uploadCellCountsPerCellLine = require("./steps/upload-cell-counts");
const uploadFileInfo = require("./steps/upload-file-info");
const uploadFileToS3 = require("./steps/upload-to-aws");
const uploadDatasetImage = require("./steps/upload-dataset-image")

const FirebaseHandler = require('../firebase/firebase-handler');

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
        name,
        version,
    } = datasetJson;
    const firebaseHandler = new FirebaseHandler(name, version);
    console.log("Dataset id:", firebaseHandler.id)
    const fileNames = {
        featureDefs: datasetJson.featureDefsPath,
        featuresData: datasetJson.featuresDataPath,
        cellLineData: datasetJson.cellLineDataPath,
    }
    for (const key in fileNames) {
        if (Object.hasOwnProperty.call(fileNames, key)) {
            if (!fileNames[key]) {
                console.error("Missing file name:", key);
                process.exit(1);
            }
        }
    }
    const readFeatureData = async () => {
        const data = await fsPromises.readFile(`${datasetReadFolder}/${fileNames.featureDefs}`)
        return JSON.parse(data)
    }

    const featureDefsData = await readFeatureData();
    const defaultGroupBy = datasetJson.defaultGroupBy;
    // 1. upload dataset description and manifest
    const manifestRef = await uploadDatasetAndManifest(firebaseHandler, datasetJson, datasetReadFolder, featureDefsData);
    // 2. check dataset feature defs for new features, upload them if needed
    const featureDefRef = await uploadFeatureDefs(firebaseHandler, featureDefsData);
    // 3. format file info, write to json locally
    await formatAndWritePerCellJsons(datasetReadFolder, TEMP_FOLDER, fileNames.featuresData, featureDefsData, defaultGroupBy);
    // 4. upload file info per cell
    const fileInfoLocation = await uploadFileInfo(firebaseHandler, TEMP_FOLDER, skipFileInfoUpload === "true");
    // 5. upload cell line subtotals
    await uploadCellCountsPerCellLine(TEMP_FOLDER, firebaseHandler, defaultGroupBy);
    // 6. upload json to aws
    const awsLocation = await uploadFileToS3(firebaseHandler.id, TEMP_FOLDER);
    // 7. upload card image
    const awsImageLocation = await uploadDatasetImage(firebaseHandler, datasetReadFolder, datasetJson.image);
    // 8. update dataset manifest with location for data
    const updateToManifest = {
        ...featureDefRef,
        ...fileInfoLocation, 
        ...awsLocation,
    }
    console.log("updating manifest", updateToManifest)
    await firebaseHandler.updateDatasetDoc({
        ...manifestRef,
        ...awsImageLocation,
    })
    await firebaseHandler.updateManifest(updateToManifest)
    process.exit(0)
}    

processDataset()
