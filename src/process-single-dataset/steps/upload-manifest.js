const dataPrep = require("../../data-validation/data-prep");
const schemas = require("../../data-validation/full-schema");

const uploadManifest = async (
  firebaseHandler,
  datasetJson,
  featureDefsData
) => {
  console.log("uploading dataset description and manifest...");

  const {
    data: manifest,
    valid,
    error,
  } = dataPrep.validate(datasetJson, schemas.manifest);
  // will be updated when the data is uploaded
  manifest.albumPath = "";
  manifest.featuresDataPath = "";
  manifest.featureDefsPath = "";
  manifest.featuresDisplayOrder = featureDefsData.map((ele) => ele.key);
  manifest.viewerSettingsPath = "";

  if (valid) {
    // upload manifest
    await firebaseHandler.uploadManifest(manifest);
  } else {
    console.log(error);
    process.exit(1);
  }
  console.log("uploading manifest complete");
  return {
    manifest: `${firebaseHandler.manifestEndpoint}/${firebaseHandler.id}`,
  };
};

module.exports = uploadManifest;
