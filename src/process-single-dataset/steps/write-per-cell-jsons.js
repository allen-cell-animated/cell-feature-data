const fsPromises = require("fs").promises;
const { find, map } = require("lodash");

const { readPossibleZippedFile } = require("../../utils");
const schemas = require("../../data-validation/full-schema");
const dataPrep = require("../../data-validation/data-prep");
const {
  FILE_INFO_KEYS,
  TEMP_LOCAL_CELL_FEATURE_JSON,
  TEMP_LOCAL_FILE_INFO_JSON,
  DEFAULT_TRANSFORM,
  REQUIRED_FILE_INFO_KEYS,
} = require("../constants");

const formatAndWritePerCellJsons = async (
  firebaseHandler,
  readFolder,
  outFolder,
  featureDataFileName,
  featureDefs,
  defaultGroupBy,
  defaultGroupByIndex
) => {
  console.log("writing out file info json...");
  const json = await readPossibleZippedFile(readFolder, featureDataFileName);
  const measuredFeaturesJson = [];
  const fileInfoJson = [];
  const counts = {};
  for (let index = 0; index < json.length; index++) {
    const cellData = json[index];
    let fileInfoKeys;
    if (cellData.file_info.length === REQUIRED_FILE_INFO_KEYS.length) {
      fileInfoKeys = REQUIRED_FILE_INFO_KEYS;
    } else if (cellData.file_info.length === FILE_INFO_KEYS.length) {
      fileInfoKeys = FILE_INFO_KEYS;
    } else {
      console.error("file info array is the wrong length");
      process.exit(1);
    }

    const fileInfo = cellData.file_info.reduce((acc, cur, index) => {
      const key = fileInfoKeys[index];
      let value = cur;
      if (key === "transform") {
        value = {
          ...DEFAULT_TRANSFORM,
          ...cur,
        };
      }
      acc[key] = value;
      return acc;
    }, {});

    const categoryValue = cellData.features[defaultGroupByIndex];
    const groupByFeature = find(featureDefs, {
      key: defaultGroupBy,
    });
    if (!groupByFeature.discrete || !groupByFeature.options) {
      console.log(`Error: defaultGroupBy \x1b[33m${defaultGroupBy}\x1b[0m, must be discrete and should have corresponding options`);
      process.exit(1);
    };
    const groupBy = groupByFeature.options[categoryValue];
    if (!groupBy) {
      console.log("NO GROUP BY FOR ", defaultGroupBy, categoryValue);
      process.exit(1);
    }
    if (!counts[categoryValue]) {
      counts[categoryValue] = 0;
    }
    counts[categoryValue]++;

    fileInfoJson[index] = fileInfo;

    measuredFeaturesJson[index] = {
      f: cellData.features,
      p: groupBy.key || groupBy.name,
      t: fileInfo.thumbnailPath,
      i: fileInfo.CellId.toString(),
    };
  }
  /* end of feature json loop */

  map(counts, (value, key) => {
    firebaseHandler.updateFeatureCount(defaultGroupBy, key, value);
  });

  const {
    data: fileInfoDoc,
    valid: fileInfoValid,
    error: fileInfoError,
  } = dataPrep.validate(fileInfoJson, schemas.fileInfo);
  const {
    data: measuredFeatureDoc,
    valid: featuresValid,
    error: featuresError,
  } = dataPrep.validate(measuredFeaturesJson, schemas.measuredFeaturesDoc);
  if (fileInfoValid && featuresValid) {
    return Promise.all([
      fsPromises.writeFile(
        `${outFolder}/${TEMP_LOCAL_CELL_FEATURE_JSON}`,
        JSON.stringify(measuredFeatureDoc)
      ),
      fsPromises.writeFile(
        `${outFolder}/${TEMP_LOCAL_FILE_INFO_JSON}`,
        JSON.stringify(fileInfoDoc)
      ),
    ]);
  } else {
    console.error("failed json validation");
    if (fileInfoError) {
      console.error("FILE INFO", fileInfoError);
    }
    if (featuresError) {
      console.error("MEASURED FEATURE", featuresError);
    }
    process.exit(1);
  }
};

module.exports = formatAndWritePerCellJsons;
