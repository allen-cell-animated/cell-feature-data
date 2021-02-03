
const fsPromises = require('fs').promises;

const FirebaseHandler = require('./firebase-handler');

const READ_FOLDER = "dataset-2-0";
const WRITE_FOLDER = "data-2-0"
const features = require(`../${WRITE_FOLDER}/measured-features`);
const writeCellFeatureData = () => {

    return fsPromises.readFile(`./${READ_FOLDER}/cell-feature-analysis.json`)
        .then((data) => JSON.parse(data))
        .then((json) => {
            Promise.all(features.map((feature) => {
                const featureName = `${feature.displayName} (${feature.unit})`
                const featureDoc = json.map((cellData) => {
                   const value = cellData.measured_features[featureName];
                   if (!value && value !== 0) {
                       console.log('feature not formatted right', featureName, cellData)
                       return Promise.resolve()
                   }
                   if (!cellData.file_info.CellId) {
                       console.log('missing id')
                       return Promise.resolve()
                   }
                   return { CellId : cellData.file_info.CellId, value: value };
               }, {})
               return fsPromises.writeFile(`${WRITE_FOLDER}/${feature.key}.json`, JSON.stringify(featureDoc))
           })).then(() => process.exit(0))
 

        })

        .catch(console.log)

}

writeCellFeatureData()