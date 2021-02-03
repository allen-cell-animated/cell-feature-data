
const fsPromises = require('fs').promises;
const map = require('lodash').map
const FirebaseHandler = require('./firebase-handler');
const {
    firestore
} = require('./setup-firebase');

const firebaseHandler = new FirebaseHandler('v1_1');

const writeBatch = (batch) => Promise.all(batch);
const ref = firestore.collection('cfe-datasets').doc('v2');
const JSON_FOLDER = "data-2-0";
const features = require(`../${JSON_FOLDER}/measured-features`);

const writeCellFeatureData = () => {

    Promise.all(features.map(async (feature) => {
        const data = await fsPromises.readFile(`${JSON_FOLDER}/${feature.key}.json`);
        const json = JSON.parse(data);
        const startingJson = json;
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