
const fsPromises = require('fs').promises;
const admin = require('firebase-admin');

const map = require('lodash').map
const features = require('../data/measured-features');
const FirebaseHandler = require('./firebase-handler');
const {
    firestore
} = require('./setup-firebase');
const PROTEIN_NAME_KEY = require('../process-dataset/constants').PROTEIN_NAME_KEY;
const CELL_LINE_NAME_KEY = require('../process-dataset/constants').CELL_LINE_NAME_KEY;
const CELL_LINE_DEF_PROTEIN_KEY = require('../process-dataset/constants').CELL_LINE_DEF_PROTEIN_KEY;
const PROTEIN_DISPLAY_NAME_KEY = require('../process-dataset/constants').PROTEIN_DISPLAY_NAME_KEY;
const CELL_LINE_DEF_STRUCTURE_KEY = require('../process-dataset/constants').CELL_LINE_DEF_STRUCTURE_KEY;
const firebaseHandler = new FirebaseHandler('v2');

const writeBatch = (batch) => Promise.all(batch);
const ref = firestore.collection('cfe-datasets').doc('v2');
const READ_JSON_FOLDER = "data-2-0"
const writeCellFeatureData = async () => {
        const data = await fsPromises.readFile(`${READ_JSON_FOLDER}/file-info.json`);
        const json = JSON.parse(data);
        const counts = json.reduce((acc, ele) => {

            const cellLine = ele.CellLineName;
            if (!acc[cellLine]) {
                acc[cellLine] = 0;
            }
            acc[cellLine]++;
            return acc;
        }, {})
        console.log(counts)
        map(counts, (value, key) => {

            ref.collection('cell-line-def').doc(key).update({
                cellCount: value
            })
        })
 
}

writeCellFeatureData()