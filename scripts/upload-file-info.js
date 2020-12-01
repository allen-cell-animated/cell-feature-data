
const fsPromises = require('fs').promises;
const map = require('lodash').map
const features = require('../data/measured-features');
const FirebaseHandler = require('./firebase-handler');
const {
    firestore
} = require('./setup-firebase');
const PROTEIN_NAME_KEY = require('../constants').PROTEIN_NAME_KEY;
const CELL_LINE_NAME_KEY = require('../constants').CELL_LINE_NAME_KEY;
const CELL_LINE_DEF_PROTEIN_KEY = require('../constants').CELL_LINE_DEF_PROTEIN_KEY;
const PROTEIN_DISPLAY_NAME_KEY = require('../constants').PROTEIN_DISPLAY_NAME_KEY;
const CELL_LINE_DEF_STRUCTURE_KEY = require('../constants').CELL_LINE_DEF_STRUCTURE_KEY;
const firebaseHandler = new FirebaseHandler('v1_1');

const writeBatch = (batch) => Promise.all(batch);
const ref = firestore.collection('cfe-datasets').doc('v1_1');

const writeCellFeatureData = async () => {
        const data = await fsPromises.readFile(`data/file-info.json`);
        const cellLineDefs = await firebaseHandler.getData('cell-line-def');
        const json = JSON.parse(data);
        const startingJson = json;
        const writeBatch = async () => {
            const batchOfData = startingJson.splice(0, 500);

            if (batchOfData.length) {
                console.log(batchOfData.length, startingJson.length)
                let batch = firestore.batch();
                batchOfData.map(cellData => {
                    const cellLineData = cellLineDefs[cellData[CELL_LINE_NAME_KEY]]
                    cellData[PROTEIN_NAME_KEY] = cellLineData[CELL_LINE_DEF_PROTEIN_KEY];
                    cellData[CELL_LINE_DEF_STRUCTURE_KEY] = cellLineData[CELL_LINE_DEF_STRUCTURE_KEY];
                    cellData[PROTEIN_DISPLAY_NAME_KEY] = cellLineData[PROTEIN_DISPLAY_NAME_KEY];
                    let docRef = ref.collection('cell-file-info').doc(cellData.CellId.toString());
                    batch.set(docRef, cellData);
                })
                await batch.commit();
                writeBatch();
            }
        }
        writeBatch()
}

writeCellFeatureData()