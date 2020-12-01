
const fsPromises = require('fs').promises;

const find = require('lodash').find;
const { CELL_ID_KEY } = require('../constants');
const features = require('../data/measured-features');
const FirebaseHandler = require('./firebase-handler');
const mapKeys = require('lodash').mapKeys;

const firebaseHandler = new FirebaseHandler('v1_1');

const writeCellFeatureData = async () => {

    return fsPromises.readFile('./cell-feature-analysis.json')
        .then((data) => JSON.parse(data))
        .then((json) => {
                const fileNameDoc = json.map((cellData) => {
                    const measuredFeatures = cellData.measured_features
                    const newKeys = mapKeys(measuredFeatures, (value, key) => {
                        let name = key.split(' (')[0];
                        let feature = find(features, {displayName : name})
                        return feature.key
                    })
                   return {[cellData.file_info[CELL_ID_KEY]]: newKeys};
               })
               return fsPromises.writeFile(`data/measured-features-per-cell.json`, JSON.stringify(fileNameDoc))
            })
 
        }

writeCellFeatureData()