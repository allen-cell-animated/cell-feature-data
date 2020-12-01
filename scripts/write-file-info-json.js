
const fsPromises = require('fs').promises;

const features = require('../data/measured-features');
const FirebaseHandler = require('./firebase-handler');

const writeCellFeatureData = () => {

    return fsPromises.readFile('./cell-feature-analysis.json')
        .then((data) => JSON.parse(data))
        .then((json) => {
                const fileNameDoc = json.map((cellData) => {
          
                   return cellData.file_info;
               })
               return fsPromises.writeFile(`data/file-info.json`, JSON.stringify(fileNameDoc))
            })
 
        }

writeCellFeatureData()