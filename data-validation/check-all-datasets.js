const fsPromises = require("fs").promises;
const Ajv = require("ajv").default;
const StreamZip = require('node-stream-zip');

const dataPrep = require("../data-validation/data-prep");

// ref schemas
const refSchemas = [
    require("./schema/definitions.schema.json"),
    require("./schema/discrete-feature-options.schema.json"),
    require("./schema/array-items/discrete-feature-option.schema.json"),
    require("./schema/array-items/file-info.schema.json"),
    require("./schema/array-items/condensed-measured-feature.schema.json"),
];

const inputMegaset = require("./schema/input-megaset.schema.json");
const inputDatasetInfo = require("./schema/input-dataset-info.schema.json");
const inputMeasuredFeatures = require("./schema/input-measured-features.schema.json");
const inputDataSet = require("./schema/input-dataset.schema.json");
const inputImages = require("./schema/images.schema.json");
const featureDef = require("./schema/feature-def.schema.json");

const ajv = new Ajv({
    coerceTypes: true,
    removeAdditional: true,
    schemas: [
        ...refSchemas,
        inputImages,
        featureDef,
        inputMegaset,
        inputDatasetInfo,
        inputMeasuredFeatures,
        inputDataSet,
    ],
});

const readDatasetJson = async (folder) => {
    const data = await fsPromises.readFile(`${folder}/dataset.json`);
    return JSON.parse(data);
};

const readFile = async (path) => {
    const data = await fsPromises.readFile(path);
    return JSON.parse(data);
};

const checkForError = (fileName, json, schemaFileName) => {
    const { valid, error } = dataPrep.validate(
        json,
        ajv.getSchema(schemaFileName)
    );
    if (!valid) {
        console.log("\x1b[0m", `${fileName}`, "\x1b[31m", `failed because: ${JSON.stringify(error)}`);
        return true;
    } else {
        console.log("\x1b[0m", `${fileName}: check against ${schemaFileName}`, "\x1b[32m", "passed");
        return false;
    }
};

const unpackInputDataset = async (datasetReadFolder) => {
    const datasetJson = await readDatasetJson(datasetReadFolder);
    const featureDefs = await readFile(
        `${datasetReadFolder}/${datasetJson.featureDefsPath}`
    );
    const images = await readFile(
        `${datasetReadFolder}/${datasetJson.viewerSettingsPath}`
    );
    let measuredFeatures;
    try {
        const data = await fsPromises.readFile(
            `${datasetReadFolder}/${datasetJson.featuresDataPath}`
        );
        measuredFeatures = JSON.parse(data);
    } catch (error) {
        const fileName = datasetJson.featuresDataPath.replace(".json", ".zip");
        const zip = new StreamZip.async({
            file: `${datasetReadFolder}/${fileName}`,
        });
        const data = await zip.entryData(`${datasetJson.featuresDataPath}`);
        measuredFeatures = JSON.parse(data);
        await zip.close();
    }
    const inputDataset = {
        dataset: datasetJson,
        "feature-defs": featureDefs,
        "measured-features": measuredFeatures,
        images: images,
    };
    return inputDataset;
}

const validateDatasets = () => {
    fsPromises.readdir("./").then(async (files) => {
        const foldersToCheck = [];
        let hasError = false;
        for (const name of files) {
            try {
                const subFiles = await fsPromises.readdir(name);
                if (subFiles.includes("dataset.json")) {
                    foldersToCheck.push(name);
                }
            } catch (error) { }
        }
        for (const datasetFolder of foldersToCheck) {
            const topLevelJson = await readDatasetJson(datasetFolder);
            if (topLevelJson.datasets) {
                const foundError = checkForError(
                    `${datasetFolder}/dataset.json`,
                    topLevelJson,
                    "input-megaset.schema.json"
                );
                if (foundError) {
                    hasError = true;
                }
                for (const subDatasetFolder of topLevelJson.datasets) {
                    const datasetReadFolder = `${datasetFolder}/${subDatasetFolder}`;
                    const inputDataset = await unpackInputDataset(datasetReadFolder)
                    const foundError = checkForError(
                        `${datasetReadFolder}`,
                        inputDataset,
                        "input-dataset.schema.json"
                    );
                    if (foundError) {
                        hasError = true;
                    }
                }
            } else {
                const inputDataset = await unpackInputDataset(datasetFolder);
                const foundError = checkForError(
                    `${datasetFolder}`,
                    inputDataset,
                    "input-dataset.schema.json"
                );
                if (foundError) {
                    hasError = true;
                }
            }
        }
        return hasError

    }).then((hasError) => {
        if (hasError) {
            console.log("\x1b[0m");
            throw Error("Validation failed");
        }
    })
}

validateDatasets();