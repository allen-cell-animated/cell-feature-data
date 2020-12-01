
const fsPromises = require('fs').promises;
const map = require('lodash').map
const features = require('../data/measured-features');
const FirebaseHandler = require('./firebase-handler');
const {
    firestore
} = require('./setup-firebase');

const firebaseHandler = new FirebaseHandler('v1_1');

const writeBatch = (batch) => Promise.all(batch);
const ref = firestore.collection('cfe-datasets').doc('v1_1');

const writeCellFeatureData = () => {

    Promise.all(features.map(async (feature) => {
        const data = await fsPromises.readFile(`data/${feature.key}.json`);
        const json = JSON.parse(data);
        const startingJson = json.slice(json.length - 26700)
        const writeBatch = async () => {
            const batchOfData = startingJson.splice(0, 500);

            if (batchOfData.length) {
                console.log(batchOfData.length, startingJson.length)
                let batch = firestore.batch();
                batchOfData.map(cellData => {
                    let docRef = ref.collection(feature.key).doc(cellData.CellId.toString());
                    batch.set(docRef, cellData);
                })
                await batch.commit();
                writeBatch();
            }
        }
        writeBatch()
  

        }))
}

writeCellFeatureData()