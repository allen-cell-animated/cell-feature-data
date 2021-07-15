const functions = require('firebase-functions');

const axios = require('axios')

const webhook = functions.config().slack.webhook

exports.postChangesToManifest = functions.firestore
    .document('manifests/{docId}')
    .onUpdate((change, context) => {
        const newValue = change.after.data();
        const previousValue = change.before.data();
        const body = {
            username: "firebase-bot",
            text: `Updated: ${JSON.stringify(context.params.docId)}, Previous value ${JSON.stringify(previousValue)}, New value: ${JSON.stringify(newValue)}`,
        }
        return axios.post(webhook, body).then(res => {
                console.log(`statusCode: ${res.status}`)
                console.log(res)
            })
            .catch(error => {
                console.error("ERROR", error.response.data)
                console.error("ERROR", error.response)

            })
    });