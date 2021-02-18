const { isEmpty, isEqual } = require('lodash');
const {
    firestore
} = require('./setup-firebase');


class FirebaseHandler {
    constructor(id) {
        this.id = id
        this.cellRef = firestore.collection('cell-data').doc(id);
    }

    uploadDatasetDoc(data) {
        return firestore.collection('dataset-descriptions').doc(data.id).set(data)
    }

    uploadManifest(data) {
        return firestore.collection("manifests").doc(this.id).set(data)
    }

    updateManifest(data) {
        return firestore.collection("manifests").doc(this.id).update(data)
    }

    uploadData(collectionName, data) {
        return firestore.collection(collectionName).doc(this.id).set(data)
    }

    getCellLineDefs() {
        return firestore.collection("cell-line-def").get()
         .then(snapshot => {
             const data = {}
             snapshot.forEach((doc) => data[doc.id] = doc.data());
             return data
         })
    }

    checkCellLineInDataset(id) {
        return this.cellRef.collection("cell-line-def").doc(id).get()
            .then(snapshot => {
                if (snapshot.exists) {

                    return snapshot.data()
                }
                return false;
            })
    }

    getData(collectionName) {
        return this.ref.collection(collectionName).get()
            .then(snapshot => {
                const data = {}
                snapshot.forEach((doc) => data[doc.id] = doc.data());
                return data
            })
    }

    checkFeatureExists(feature) {
        return firestore.collection("feature-definitions").doc(feature.key).get()
            .then(snapshot => {
                if (snapshot.exists ) {
                    const changedFeatures = {}
                    const dbFeature = snapshot.data();
                    for (const key in feature) {
                        if (Object.hasOwnProperty.call(feature, key)) {
                            const newValue = feature[key];
                            if (!isEqual( dbFeature[key], newValue)) {
                                changedFeatures[key] = newValue
                            }
                        }
                    }
                    if (isEmpty(changedFeatures)) {
                        return false
                    }
                    return changedFeatures;
                } else {
                    return false;
                }
            })
    }

    addFeature(feature) {
        return firestore.collection("feature-definitions").doc(feature.key).set(feature)

    }

    checkData(collectionName, docName, dataKey, dataValue) {
        return this.ref.collection(collectionName).doc(docName).get()
        .then(snapshot => {
            const data = snapshot.data();
            return data[dataKey] === dataValue;
        })
    }

    uploadArrayUsingFirebaseIds(array, collectionName) {
        return Promise.all(array.map((ele) => this.ref.collection(collectionName).add(ele)))
    }
    uploadArrayUsingKeys(array, collectionName, docKey) {
        return Promise.all(array.map((ele) => firestore.collection(collectionName).doc(ele[docKey]).set(ele)))
    }
    setData(collectionName, docName, data) {
        return this.ref.collection(collectionName).doc(docName).set(data).catch((e) => console.log(collectionName, docName, e))
    }
    writeData(collectionName, docName, data) {
        return this.ref.collection(collectionName).doc(docName).update(data).catch((e) => console.log(collectionName, docName, e))
    }
}

module.exports = FirebaseHandler;