const fsPromises = require('fs').promises;
const uploadDatasetAndManifest = require("./upload-dataset-and-manifest")
const args = process.argv.slice(2);
console.log('myArgs: ', args);

const datasetReadFolder = args[0];


const readDatasetInfo = async () => {
    const data = await fsPromises.readFile(`${datasetReadFolder}/dataset.json`)
    return JSON.parse(data)
}

const processDataset = async () => {

    if (!datasetReadFolder) {
        console.log("NEED A DATASET FOLDER TO PROCESS")
        process.exit(1)
    }
    
    fsPromises.readdir(datasetReadFolder)
        .catch ((error) => {
            console.log("COULDN'T READ DIRECTORY:", error)
        })
    
    const datasetJson = await readDatasetInfo()
    const {
        id
    } = datasetJson;
    console.log(id)
    await uploadDatasetAndManifest(datasetJson, datasetReadFolder)
    process.exit(0)
}    

processDataset()
