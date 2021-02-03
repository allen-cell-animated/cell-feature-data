
const fsPromises = require('fs').promises;

const find = require('lodash').find;
const { CELL_ID_KEY } = require('../constants');
const mapKeys = require('lodash').mapKeys;

const JSON_READ_FOLDER = "dataset-2-0";
const JSON_WRITE_FOLDER = "data-2-0";
const features = require(`../${JSON_WRITE_FOLDER}/measured-features`);

const writeCellFeatureData = async () => {

    return fsPromises.readFile(`./${JSON_READ_FOLDER}/cell-feature-analysis.json`)
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
               return fsPromises.writeFile(`${JSON_WRITE_FOLDER}/measured-features-per-cell.json`, JSON.stringify(fileNameDoc))
            })
 
        }

writeCellFeatureData()