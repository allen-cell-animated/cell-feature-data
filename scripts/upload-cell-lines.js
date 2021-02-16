const fsPromises = require('fs').promises;
const prompt = require('prompt');
const {
    mapKeys
} = require('lodash');


const FirebaseHandler = require('./firebase-handler');
const READ_FOLDER = "dataset-2-1";


const readDatasetInfo = async () => {
    const data = await fsPromises.readFile(`./${READ_FOLDER}/dataset.json`)
    return JSON.parse(data)
}

const formatCellLineDefs = () => (
    fsPromises.readFile(`./${READ_FOLDER}/cell_line_def.json`)
    .then((data) => JSON.parse(data))
    .then((json) => json.map((ele) => mapKeys(ele, (value, key) => key.replace('/', '_'))))
)

const writeCellLineDefs = async () => {
    const dataset = await readDatasetInfo();
    const id = dataset.id
    const firebaseHandler = new FirebaseHandler(id);
    return formatCellLineDefs()
        .then((json) => firebaseHandler.uploadArrayUsingKeys(json, "cell-line-def", "CellLineId_Name"))
        .then(() => process.exit(0))

}

writeCellLineDefs()
