const fsPromises = require("fs").promises;
const StreamZip = require('node-stream-zip');

const readAndParseFile = async (path) => {
    const data = await fsPromises.readFile(path);
    return JSON.parse(data);
};

const readDatasetJson = async (folder) => {
    const path = `${folder}/dataset.json`;
    return await readAndParseFile(path);
};

const readPossibleZippedFile = async (folder, fileName) => {
    let parsedData;
    try {
        const data = await fsPromises.readFile(
            `${folder}/${fileName}`
        );
        parsedData = JSON.parse(data);
    } catch (error) {
        if (error.message.includes("no such file or directory")) {
            try {
                const zipFileName = fileName.replace(".json", ".zip");
                const zip = new StreamZip.async({
                    file: `${folder}/${zipFileName}`,
                });
                const data = await zip.entryData(fileName);
                parsedData = JSON.parse(data);
                await zip.close();
            } catch (error) {
                console.log("Was unable to find a json file, or open a zip file", error);
                process.exit(1);
            }
        } else {
            console.log("Was unable to read the JSON file", error);
            process.exit(1);
        }
    }
    return parsedData;
}

const validateFeatureDataKeys = (featuresDataOrder, featureDefs) => {
    const keyList = Array.from(featureDefs, (featureDataJson) => featureDataJson.key);
    if (featuresDataOrder.length > keyList.length) {
        const keysErrorMsg = 
            `Error: featureDefs has ${keyList.length} features but there are ${featuresDataOrder.length} listed in featuresDataOrder`;
        return { featureKeysError: true, keysErrorMsg };
    };
    for (const keyName of featuresDataOrder) {
        if (!keyList.includes(keyName)) {
            const keysErrorMsg =
                `Error: key ${keyName} in featuresDataOrder does not exist in featureDefs`;
            return { featureKeysError: true, keysErrorMsg };
        }
    }
    return { featureKeysError: false, keysErrorMsg: "" };
};

const validateUserDataValues = (totalCells, totalFOVs) => {
    if (!totalCells && !totalFOVs) {
        const userDataErrorMsg = "Error: totalCells and totalFOVs can't both be zero or undefined";
        return { userDataError: true, userDataErrorMsg };
    }
    return { userDataError: false, userDataErrorMsg: "" };
};

const validateKeyInOptions = (options) => {
    const uniqueNames = new Set();

    for (const option of options) {
        if (uniqueNames.has(option.name) && !option.key) {
            const optionKeyErrorMsg = `Error: option ${option.name} is not unique, key is required`;
            return { optionKeyError: true, optionKeyErrorMsg };
        }
        uniqueNames.add(option.name);
    }
    return { optionKeyError: false, optionKeyErrorMsg: "" };
};

const validateFeatureDataOptions = (featureDefsData) => {
    for (let featureDef of featureDefsData) {
        if (featureDef.options){
            const options = Object.values(featureDef.options);
            const {optionKeyError, optionKeyErrorMsg} = validateKeyInOptions(options);
            if (optionKeyError) {
                return { optionKeyError, optionKeyErrorMsg };
            }
        }
    }
    return { optionKeyError: false, optionKeyErrorMsg: "" };
};


module.exports = {
    readDatasetJson,
    readAndParseFile, 
    readPossibleZippedFile,
    validateFeatureDataKeys,
    validateUserDataValues,
    validateFeatureDataOptions,
}