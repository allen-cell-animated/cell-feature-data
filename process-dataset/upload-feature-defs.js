const fsPromises = require('fs').promises;
const prompt = require('prompt');

const dataPrep = require("../scripts/data-prep");

const FirebaseHandler = require('../scripts/firebase-handler');

const schemas = require("../scripts/schema");

const readFeatureData = async (readFolder) => {
    const data = await fsPromises.readFile(`${readFolder}/feature_defs.json`)
    return JSON.parse(data)
}

const uploadFeatureDefs = async (firebaseHandler, readFolder) => {
    console.log("uploading feature defs...")
    const featureDefs = await readFeatureData(readFolder);
    for (let index = 0; index < featureDefs.length; index++) {
        const feature = featureDefs[index];

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
                await firebaseHandler.addFeature(feature)
            }



        } else if (featureCheck.valid) {
            await firebaseHandler.addFeature(feature)
        }

    }
    console.log("uploading feature defs complete")


}

module.exports = uploadFeatureDefs