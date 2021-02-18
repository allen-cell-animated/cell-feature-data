const fsPromises = require('fs').promises;

const {
    firestore
} = require('../scripts/setup-firebase');
const PROTEIN_NAME_KEY = require('./constants').PROTEIN_NAME_KEY;
const CELL_LINE_NAME_KEY = require('./constants').CELL_LINE_NAME_KEY;
const CELL_LINE_DEF_PROTEIN_KEY = require('./constants').CELL_LINE_DEF_PROTEIN_KEY;
const PROTEIN_DISPLAY_NAME_KEY = require('./constants').PROTEIN_DISPLAY_NAME_KEY;
const CELL_LINE_DEF_STRUCTURE_KEY = require('./constants').CELL_LINE_DEF_STRUCTURE_KEY;


const uploadFileInfo = async (firebaseHandler, readFolder) => {
    console.log("uploading file info...")
    const data = await fsPromises.readFile(`${readFolder}/file-info.json`);
    const cellLineDefs = await firebaseHandler.getCellLineDefs();
    const json = JSON.parse(data);
    const startingJson = json.splice(json.length - 224);
    const writeBatch = async () => {
        const batchOfData = startingJson.splice(0, 498); // max is 500, at most a batch of this size will have 2 cell lines to upload
        if (batchOfData.length) {
            const newCellLinesThisBatch = [];
            console.log(batchOfData.length, startingJson.length)
            const batch = firestore.batch();
            for (let index = 0; index < batchOfData.length; index++) {
                const cellData = batchOfData[index];

                const cellLine = cellData[CELL_LINE_NAME_KEY];
                const cellLineData = cellLineDefs[cellLine]
                cellData[PROTEIN_NAME_KEY] = cellLineData[CELL_LINE_DEF_PROTEIN_KEY];
                cellData[CELL_LINE_DEF_STRUCTURE_KEY] = cellLineData[CELL_LINE_DEF_STRUCTURE_KEY];
                cellData[PROTEIN_DISPLAY_NAME_KEY] = cellLineData[PROTEIN_DISPLAY_NAME_KEY];

                const cellLineInDb = await firebaseHandler.checkCellLineInDataset(cellLine)
                if (!cellLineInDb && !newCellLinesThisBatch.includes(cellLine)) {
                    console.log("adding cell line", cellLine)
                    newCellLinesThisBatch.push(cellLine)
                    batch.set(firebaseHandler.cellRef.collection("cell-line-def").doc(cellLine), cellLineData)
                }
                const docRef = firebaseHandler.cellRef.collection('cell-file-info').doc(cellData.CellId.toString());
                batch.set(docRef, cellData);
            }

            await batch.commit().catch(console.log);
            await writeBatch();

        }
    }
    await writeBatch();
    console.log("uploading file info complete")
    return {
        cellLineData: `cell-data/${firebaseHandler.id}/cell-line-def`
    }
}

module.exports = uploadFileInfo;