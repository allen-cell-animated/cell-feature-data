
const fsPromises = require('fs').promises;

const writeCellFeatureData = () => {

    return fsPromises.readFile('./dataset-2-0/cell-feature-analysis.json')
        .then((data) => JSON.parse(data))
        .then((json) => {
                const fileNameDoc = json.map((cellData) => {
          
                   return cellData.file_info;
               })
               return fsPromises.writeFile(`data-2-0/file-info.json`, JSON.stringify(fileNameDoc))
            })
 
        }

writeCellFeatureData()