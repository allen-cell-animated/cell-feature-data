const fsPromises = require('fs').promises;

const keys = [
    "CellId",
    "FOVId",
    "CellLineName",
    "thumbnailPath",
    "volumeviewerPath",
    "fovThumbnailPath",
    "fovVolumeviewerPath"
]


const formatAndWriteFileInfoJson = async (readFolder, outFolder) => {

    console.log("writing out file info json...")
    return fsPromises.readFile(`${readFolder}/cell_feature_analysis.json`)
        .then((data) => JSON.parse(data))
        .then((json) => {
            const fileNameDoc = json.map((cellData) => {
                if (cellData.file_info.length !== keys.length) {
                    console.log("file info in not in expected format")
                    process.exit(1)
                }
                return cellData.file_info.reduce((acc, cur, index) =>  {
                    
                    acc[keys[index]] = cur
                    return acc;
                }, {});
            })
            return fsPromises.writeFile(`${outFolder}/file-info.json`, JSON.stringify(fileNameDoc))
        })
        .then(() => {
            console.log("writing out file info json complete")
        })

}

module.exports = formatAndWriteFileInfoJson