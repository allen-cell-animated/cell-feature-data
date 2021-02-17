
const fsPromises = require('fs').promises;

const {
    firestore
} = require('./setup-firebase');
const PROTEIN_NAME_KEY = require('../constants').PROTEIN_NAME_KEY;
const CELL_LINE_NAME_KEY = require('../constants').CELL_LINE_NAME_KEY;
const CELL_LINE_DEF_PROTEIN_KEY = require('../constants').CELL_LINE_DEF_PROTEIN_KEY;
const PROTEIN_DISPLAY_NAME_KEY = require('../constants').PROTEIN_DISPLAY_NAME_KEY;
const CELL_LINE_DEF_STRUCTURE_KEY = require('../constants').CELL_LINE_DEF_STRUCTURE_KEY;


const writeCellFeatureData = async (firebaseHandler, readFolder) => {
        const data = await fsPromises.readFile(`${readFolder}/file-info.json`);
        const cellLineDefs = await firebaseHandler.getCellLineDefs();
        const json = JSON.parse(data);
        const startingJson = json;
        const writeBatch = async () => {
            const batchOfData = startingJson.splice(0, 500);

            if (batchOfData.length) {
                console.log(batchOfData.length, startingJson.length)
                let batch = firestore.batch();
                batchOfData.map(async cellData => {
                    const cellLine = cellData[CELL_LINE_NAME_KEY];
                    const cellLineData = cellLineDefs[cellLine]
                    cellData[PROTEIN_NAME_KEY] = cellLineData[CELL_LINE_DEF_PROTEIN_KEY];
                    cellData[CELL_LINE_DEF_STRUCTURE_KEY] = cellLineData[CELL_LINE_DEF_STRUCTURE_KEY];
                    cellData[PROTEIN_DISPLAY_NAME_KEY] = cellLineData[PROTEIN_DISPLAY_NAME_KEY];

                    let docRef = firebaseHandler.cellRef.collection('cell-file-info').doc(cellData.CellId.toString());
                    const cellLine = await firebaseHandler.checkCellLineInDataset(cellLine)
                    if (!cellLine) {
                        batch.update(this.cellRef.collection("cell-line-def").doc(cellLine), cellLineData)
                    }
                    batch.update(docRef, cellData);
                })
                await batch.commit();
                writeBatch();
            }
        }
        writeBatch()
}

writeCellFeatureData()