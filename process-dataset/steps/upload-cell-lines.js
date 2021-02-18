const fsPromises = require('fs').promises;
const {
    mapKeys
} = require('lodash');

const formatCellLineDefs = (readFolder) => (
    fsPromises.readFile(`${readFolder}/cell_line_def.json`)
    .then((data) => JSON.parse(data))
    .then((json) => json.map((ele) => mapKeys(ele, (value, key) => key.replace('/', '_'))))
)

const uploadCellLines = async (firebaseHandler, readFolder) => {
    console.log("uploading cell lines..." )
    return formatCellLineDefs(readFolder)
        .then((json) => firebaseHandler.uploadArrayUsingKeys(json, "cell-line-def", "CellLineId_Name"))
        .then(() => console.log("uploading cell lines complete"))
}

module.exports = uploadCellLines;