const fsPromises = require('fs').promises;

const map = require('lodash').map


const uploadCellCountsPerCellLine = async (readFolder, firebaseHandler) => {
    console.log("uploading cell line counts... ")
    const data = await fsPromises.readFile(`${readFolder}/file-info.json`);
    const json = JSON.parse(data);
    const counts = json.reduce((acc, ele) => {

        const cellLine = ele.CellLineName;
        if (!acc[cellLine]) {
            acc[cellLine] = 0;
        }
        acc[cellLine]++;
        return acc;
    }, {})
    map(counts, (value, key) => {

        firebaseHandler.cellRef.collection('cell-line-def').doc(key).update({
            cellCount: value
        })
    })
    console.log("uploading cell line counts complete ")

}

module.exports = uploadCellCountsPerCellLine