const fsPromises = require('fs').promises;
const prompt = require('prompt');

const dataPrep = require("../scripts/data-prep");

const FirebaseHandler = require('../scripts/firebase-handler');

const schemas = require("../scripts/schema");

const readFeatureData = async (readFolder) => {
    const data = await fsPromises.readFile(`${readFolder}/feature_defs.json`)
    return JSON.parse(data)
}

const uploadFeatureDefs = async (datasetId, readFolder) => {
    const featureDefs = await readFeatureData(readFolder);
    for (let index = 0; index < featureDefs.length; index++) {
        const feature = featureDefs[index];
        
        const firebaseHandler = new FirebaseHandler(datasetId);
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

module.exports = uploadFeatureDefs