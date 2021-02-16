const {
    firestore
} = require('./setup-firebase');


class FirebaseHandler {
    constructor(id) {
        this.id = id
        this.ref = firestore.collection('cfe-datasets').doc(id);
    }

    uploadDatasetDoc(data) {
        return firestore.collection('dataset-descriptions').doc(data.id).set(data)
    }

    uploadManifest(data) {
        return firestore.collection("manifests").doc(this.id).set(data)
    }

    getData(collectionName) {
        return this.ref.collection(collectionName).get()
            .then(snapshot => {
                const data = {}
                snapshot.forEach((doc) => data[doc.id] = doc.data());
                return data
            })
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
        return Promise.all(array.map((ele) => this.ref.collection(collectionName).doc(ele[docKey]).set(ele)))
    }
    setData(collectionName, docName, data) {
        return this.ref.collection(collectionName).doc(docName).set(data).catch((e) => console.log(collectionName, docName, e))
    }
    writeData(collectionName, docName, data) {
        return this.ref.collection(collectionName).doc(docName).update(data).catch((e) => console.log(collectionName, docName, e))
    }
}

module.exports = FirebaseHandler;