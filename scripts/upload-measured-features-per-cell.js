
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
        const json = await fsPromises.readFile(`data/measured-features-per-cell.json`);
        const data = JSON.parse(json);
        const writeBatch = async () => {
            const batchOfData = data.splice(0, 500);

            if (batchOfData.length) {
                console.log(batchOfData.length, data.length)
                let batch = firestore.batch();
                batchOfData.map(cellData => {
                    const id = Object.keys(cellData)[0]
                    let docRef = ref.collection('measured-features-values').doc(id);
                    batch.set(docRef, cellData[id]);
                })
                await batch.commit();
                writeBatch();
            }
        }
        writeBatch()
}

writeCellFeatureData()