const fsPromises = require('fs').promises;
const dataPrep = require("./data-prep");

const FirebaseHandler = require('./firebase-handler');
const READ_FOLDER = "dataset-2-1";

const schemas = require("./schema");

const readFeatureData = async () => {
    const data = await fsPromises.readFile(`./${READ_FOLDER}/feature_defs.json`)
    return JSON.parse(data)
}
const uploadDatasetAndManifest = () => {

    return fsPromises.readFile(`./${READ_FOLDER}/dataset.json`)
        .then((data) => JSON.parse(data))
        .then(async (json) => {
            const featureData = await readFeatureData();
            const dataset = dataPrep.initialize(json, schemas.datasetSchema)
            const firebaseHandler = new FirebaseHandler(dataset.id)

            const manifest = dataPrep.initialize(json, schemas.manifestSchema)
            // will be updated when the data is uploaded
            manifest.cellLineData = "";
            manifest.albumPath = "";
            manifest.featuresData = "";

            manifest.featuresDisplayOrder = featureData.map(ele => ele.key)
            const datasetCheck = dataPrep.validate(dataset, schemas.dataset)
            const manifestCheck = dataPrep.validate(manifest, schemas.manifest)
            if (datasetCheck.valid) {
                // upload dataset
                firebaseHandler.uploadDatasetDoc(dataset)
            } else {
                console.log(datasetCheck.error)
            }
            if (manifestCheck.valid) {
                // upload manifest
                firebaseHandler.uploadManifest(manifest)
            } else {
                console.log(manifestCheck.error)
            }
        })

        .catch(console.log)

}

uploadDatasetAndManifest()