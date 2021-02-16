const fsPromises = require('fs').promises;
const prompt = require('prompt');

const dataPrep = require("./data-prep");

const FirebaseHandler = require('./firebase-handler');
const READ_FOLDER = "dataset-2-1";

const schemas = require("./schema");

const readFeatureData = async () => {
    const data = await fsPromises.readFile(`./${READ_FOLDER}/feature_defs.json`)
    return JSON.parse(data)
}

const readDatasetInfo = async () => {
    const data = await fsPromises.readFile(`./${READ_FOLDER}/dataset.json`)
    return JSON.parse(data)
}

const uploadFeatureDefs = async () => {
    const featureDefs = await readFeatureData();
    const dataset = await readDatasetInfo();
    for (let index = 0; index < featureDefs.length; index++) {
        const feature = featureDefs[index];
        
        const firebaseHandler = new FirebaseHandler(dataset.id);
        const featureData = dataPrep.initialize(feature, schemas.featureDefSchema)
        const diffToDatabase = await firebaseHandler.checkFeatureExists(featureData)
        const featureCheck = dataPrep.validate(featureData, schemas.featureDef)
        if (diffToDatabase && featureCheck.valid) {
            prompt.start();
            console.log(`feature "${feature.key}" is already in db`)
            for (const key in diffToDatabase) {
                if (Object.hasOwnProperty.call(diffToDatabase, key)) {
                    const element = diffToDatabase[key];
                    console.log(`${key} DB VALUE: ${element}, NEW VALUE: ${featureData[key]}`)
                }
            }
            console.log("Do you want to over write what is in the DB? (Y/N)")
            const {
                shouldWrite
            } = await prompt.get(['shouldWrite']);
            if (shouldWrite.toLowerCase() === "y") {
                firebaseHandler.addFeature(feature)
            }

        
            
        } else if (featureCheck.valid) {
            firebaseHandler.addFeature(feature)
        }
    }
    process.exit(0)
    


}

uploadFeatureDefs()