const fsPromises = require('fs').promises;
const {
    mapKeys
} = require('lodash');

const formatCellLineDefs = (readFolder, cellLineDefFileName) => (
    fsPromises.readFile(`${readFolder}/${cellLineDefFileName}`)
    .then((data) => JSON.parse(data))
    .then((json) => json.map((ele) => mapKeys(ele, (value, key) => key.replace('/', '_'))))
)

const uploadCellLines = async (firebaseHandler, readFolder, cellLineDefFileName) => {
    console.log("uploading cell lines..." )
    const json = await formatCellLineDefs(readFolder, cellLineDefFileName)

    await firebaseHandler.uploadArrayUsingKeys(json, "cell-line-def", "CellLineId_Name")
    console.log("uploading cell lines complete")
    return json;
}

module.exports = uploadCellLines;