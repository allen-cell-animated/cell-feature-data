const fsPromises = require('fs').promises;
const dataPrep = require("./data-validation/data-prep");
const schemas = require("./data-validation/schema");

const uploadDatasetAndManifest = async (firebaseHandler, datasetJson, readFolder) => {
    console.log("uploading dataset description and manifest...");
    const readFeatureData = async () => {
        const data = await fsPromises.readFile(`${readFolder}/feature_defs.json`)
        return JSON.parse(data)
    }

    const featureData = await readFeatureData();
    const dataset = dataPrep.initialize(datasetJson, schemas.datasetSchema)

    const manifest = dataPrep.initialize(datasetJson, schemas.manifestSchema)
    // will be updated when the data is uploaded
    manifest.cellLineData = "";
    manifest.albumPath = "";
    manifest.featuresData = "";

    manifest.featuresDisplayOrder = featureData.map(ele => ele.key)
    const datasetCheck = dataPrep.validate(dataset, schemas.dataset)
    const manifestCheck = dataPrep.validate(manifest, schemas.manifest)
    if (datasetCheck.valid) {
        // upload dataset
        await firebaseHandler.uploadDatasetDoc(dataset)
    } else {
        console.log(datasetCheck.error)
    }
    if (manifestCheck.valid) {
        // upload manifest
        await firebaseHandler.uploadManifest(manifest)
    } else {
        console.log(manifestCheck.error)
    }
    console.log("uploading dataset description and manifest complete");



}

module.exports = uploadDatasetAndManifest;