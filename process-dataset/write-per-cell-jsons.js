const fsPromises = require('fs').promises;
const schemas = require("./data-validation/schema");
const dataPrep = require ("./data-validation/data-prep");
const {
    find
} = require("lodash");
const {
    CELL_LINE_NAME_KEY,
    PROTEIN_DISPLAY_NAME_KEY,
    FILE_INFO_KEYS
} = require("./constants");


const readCellLines = (readFolder) => (
    fsPromises.readFile(`${readFolder}/cell_line_def.json`)
    .then((data) => JSON.parse(data))
)


const formatAndWritePerCellJsons = async (readFolder, outFolder) => {

    console.log("writing out file info json...")
    return fsPromises.readFile(`${readFolder}/cell_feature_analysis.json`)
        .then((data) => JSON.parse(data))
        .then(async (json) => {
            const cellLines = await readCellLines(readFolder);
            const measuredFeaturesJson = [];
            const fileInfoJson = [];
            for (let index = 0; index < json.length; index++) {
                const cellData = json[index];
                
                if (cellData.file_info.length !== FILE_INFO_KEYS.length) {
                    console.error("file info in not in expected format")
                    process.exit(1)
                }
                const fileInfo = cellData.file_info.reduce((acc, cur, index) => {
                    
                    acc[FILE_INFO_KEYS[index]] = cur;
                    return acc;
                }, {});
                fileInfoJson[index] = fileInfo;
                const cellLine = find(cellLines, {
                            "CellLineId/Name" : fileInfo[CELL_LINE_NAME_KEY]});
                if (!cellLine) {
                    console.error("No matching cell line for this cell in the dataset", fileInfo)
                    process.exit(1)
                }
                measuredFeaturesJson[index] = {
                    f: cellData.features,
                    p: cellLine["ProteinId/DisplayName"],
                    t: fileInfo.thumbnailPath
                }

            }
            
            fileInfoJson.forEach(fileInfo => {

                const fileInfoCheck = dataPrep.validate(fileInfo, schemas.fileInfo);
                if (!fileInfoCheck.valid) {
                    console.error("file info didn't match expected schema", fileInfoCheck.error, fileInfo)
                    process.exit(1)
                }
            })
            return Promise.all([fsPromises.writeFile(`${outFolder}/cell-feature-analysis.json`, JSON.stringify(measuredFeaturesJson)),
             fsPromises.writeFile(`${outFolder}/file-info.json`, JSON.stringify(fileInfoJson))])
        })
        .then(() => {
            console.log("writing out file info json complete")
        })

}

module.exports = formatAndWritePerCellJsons