const Ajv = require("ajv").default
const ajv = new Ajv() // options can be passed, e.g. {allErrors: true}

const datasetSchema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "datasetSchema",
    "title": "Dataset",
    "description": "Data needed to render a dataset card",
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "name": {
            "description": "Name of the dataset",
            "type": "string"
        },
        "id": {
              "description": "Id for the dataset",
              "type": "string"
        },
        "version": {
            "description": "version year and number",
            "type": "string",
        },
        "description": {
            "description": "Description of the dataset",
            "type": "string",
        },
        "image": {
            "description": "Url to image src",
            "type": "string",
        },
        "link": {
            "description": "Link to website displaying the dataset",
            "type": "string",
        },
        "userData": {
            "description": "Optional display data",
            "type": "object",
        },
    },
    "required": [
        "name",
        "version",
        "id",
        "image",
        "description",
       
    ],
}

const manifestSchema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "manifestSchema",
    "title": "Manifest",
    "description": "High level for each dataset",
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "featuresData": {
            "description": "url to the per cell data json",
            "type": "string"
        },
        "cellLineData": {
            "description": "collection name of the cell line data",
            "type": "string",
        },
        "albumPath": {
            "description": "collection name of the album data",
            "type": "string",
        },
        "thumbnailRoot": {
            "description": "Root url for thumbnail images",
            "type": "string",
        },
        "downloadRoot": {
            "description": "Root url for downloading cell data",
            "type": "string",
        },
        "volumeViewerDataRoot": {
            "description": "Root url for 3d images",
            "type": "string",
        },
        "defaultXAxis": {
            "description": "Default feature to plot on x axis",
            "type": "string",
        },
        "defaultYAxis": {
            "description": "Default feature to plot on y axis",
            "type": "string",
        },
        "featuresDisplayOrder": {
            "description": "Ordered array of feature keys",
            "type": "array",
        },
    },
    "required": [
        "featuresData",
        "cellLineData",
        "albumPath",
        "thumbnailRoot",
        "downloadRoot",
        "volumeViewerDataRoot",
        "defaultXAxis",
        "defaultYAxis",
        "featuresDisplayOrder"
    ],
}

module.exports = {
    datasetSchema: datasetSchema,
    manifestSchema: manifestSchema,
    dataset: ajv.compile(datasetSchema),
    manifest: ajv.compile(manifestSchema),
}
