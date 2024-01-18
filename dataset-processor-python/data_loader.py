import json
from pathlib import Path
import re
import sys
import csv
import numpy
import pandas as pd
import questionary
from user_input_handler import UserInputHandler


class DataLoader:
    """
    Loads the csv file and stores the initial data
    """

    def __init__(self, inputs):
        self.inputs = inputs
        self.data = self.load_csv()

    def load_csv(self):
        """
        Read the csv file and store the data
        Returns a list of dictionaries, where each dictionary represents a row in the csv file
        """
        try:
            with open(self.inputs["path"], "r") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error while reading CSV: {e}")
            return None


# global constants
CELL_FEATURE_ANALYSIS_FILENAME = "cell_feature_analysis.json"
DATASET_FILENAME = "dataset.json"
FEATURE_DEFS_FILENAME = "feature_defs.json"
IMAGE_SETTINGS_FILENAME = "image_settings.json"

FILEINFO_COLUMN_NAMES = [
    "cell_id",
    "parent_id",
    "cell_group",
    "cell_thumbnail",
    "cell_image",
    "parent_thumbnail",
    "parent_image",
]


class DatasetDoc:
    """
    Class to store data for the dataset.json
    """

    # default values for the dataset.json file
    title = ""
    image = ""
    description = ""
    album_path = ""
    thumbnail_root = ""
    download_root = ""
    volume_viewer_data_root = ""
    xAxis = {"default": "", "exclude": []}
    yAxis = {"default": "", "exclude": []}
    color_by = {"default": ""}
    group_by = {"default": ""}
    features_display_order = []

    def __init__(self, inputs):
        self.inputs = inputs
        self.dataset_data = {}

    def compile_dataset(self, features_data_order):
        required_fields_to_write = {
            "title": self.title,
            "version": self.inputs["version"],
            "name": self.inputs["dataset_name"],
            "image": self.image,
            "description": self.description,
            "featureDefsPath": FEATURE_DEFS_FILENAME,
            "featuresDataPath": CELL_FEATURE_ANALYSIS_FILENAME,
            "viewerSettingsPath": IMAGE_SETTINGS_FILENAME,
            "albumPath": self.album_path,
            "thumbnailRoot": self.thumbnail_root,
            "downloadRoot": self.download_root,
            "volumeViewerDataRoot": self.volume_viewer_data_root,
            "xAxis": self.xAxis,
            "yAxis": self.yAxis,
            "colorBy": self.color_by,
            "groupBy": self.group_by,
            "featuresDisplayOrder": self.features_display_order,
            "featuresDataOrder": features_data_order,
        }
        self.dataset_data.update(required_fields_to_write)


class CellFeatureDoc:
    """
    Class to store data for the cell_feature_analysis.json
    """

    def __init__(self):
        self.cell_feature_analysis_data = []

    @staticmethod
    def convert_str_to_num(value):
        try:
            numeric_value = float(value)
            if numeric_value.is_integer():
                return int(numeric_value)
            return numeric_value
        except ValueError:
            # if not number, return the original value
            return value

    def compile_cell_feature_analysis(self, file_info, features):
        self.cell_feature_analysis_data.append(
            {"file_info": file_info, "features": features}
        )


class FeatureDefsDoc:
    """
    Class to store data for the feature_defs.json
    """

    def __init__(self, data, inputs):
        self.data = data
        self.inputs = inputs
        self.feature_defs_data = []

        # self.feature_def_keys is a list of feature names(with units if applicable) in order of appearance in the csv file
        self.feature_def_keys = []
        # self.feature_discreteness_map is a dictionary of feature names and whether they are discrete or not
        # e.g. {"feature1": True, "feature2": False}
        self.feature_discreteness_map = {}
        # self.features_data_order is a list of feature names(without units) in order of appearance in the csv file
        self.features_data_order = []
        # self.discrete_features is a list of discrete feature names
        self.discrete_features = []

    @staticmethod
    def is_valid_feature_value(value):
        return pd.isna(value) or isinstance(value, (int, float))

    @staticmethod
    def is_discrete(numeric_value):
        """
        Determines if the numeric value is discrete
        """
        return not pd.isna(numeric_value) and numeric_value == int(numeric_value)

    @staticmethod
    def get_unit(key):
        """
        Extracts the unit from the key if present
        """
        match = re.search(r"\((.*?)\)$", key)
        return match.group(1) if match else ""

    @staticmethod
    def format_display_name(title):
        """
        Formats the title to display name, e.g. "the-title-of-the-feature" -> "The Title of the Feature"
        """
        title = title.replace("-", " ")
        lowercase_list = ["the", "for", "in", "of", "on", "to", "and", "as", "or"]
        title_words = title.split()
        return " ".join(
            word if (word in lowercase_list and i != 0) else word.title()
            for i, word in enumerate(title_words)
        )

    @staticmethod
    def get_color(index):
        colors = [
            "#A6CEE3",
            "#1F78B4",
            "#B2DF8A",
            "#33A02C",
            "#FB9A99",
            "#E31A1C",
            "#FDBF6F",
            "#FF7F00",
            "#CAB2D6",
        ]
        if index >= len(colors):
            index = index % len(colors)
        return colors[index]

    def update_feature_metadata(self, column, value):
        """
        Updates the feature metadata with whether the feature is discrete or not
        Store the list of original feature names for writing the feature defs file
        """
        is_discrete = self.is_discrete(value)
        if (
            column in self.feature_discreteness_map
            and is_discrete != self.feature_discreteness_map[column]
        ):
            print(
                f"Column {column} has both discrete and continuous values. Please make sure that all values in a column are either discrete or continuous."
            )
            return
        self.feature_discreteness_map[column] = is_discrete
        if column not in self.feature_def_keys:
            self.feature_def_keys.append(column)

    def process_features(self, column, value, features):
        if self.is_valid_feature_value(value):
            features.append(value)
            self.update_feature_metadata(column, value)
        else:
            print(f"Invalid value: {value} in column {column}")
            return

    def get_column_data(self, column):
        """
        Returns the column data from the dataset
        """
        column_data = []
        for row in self.data:
            column_data.append(row.get(column, ""))
        return column_data

    def write_discrete_feature_options(self, data_values):
        """
        Keys in options are the unique values in the column, and values are the color and name of the feature
        Returns the options for a discrete feature

        Options example:
        "options":{
            "7": {
                "color": "#FF96FF",
                "name": "Actin filaments",
                "key": "Alpha-actinin-1"
            },
            "16": {
                "color": "#FFB1FF",
                "name": "Actin filaments",
                "key": "Beta-actin"
        }
        """
        keys = numpy.unique(data_values)
        options = {}
        for index, key in enumerate(keys):
            # "key" is optional, if "name" is not unique, use "key" to distinguish between the options
            options[key] = {"color": self.get_color(index), "name": key, "key": key}
        return options

    def compile_feature_defs(self):
        description = ""
        tooltip = ""
        for key in self.feature_def_keys:
            discrete = self.feature_discreteness_map[key]
            unit = self.get_unit(key)
            stripped_key = key.replace(f"({unit})", "").strip()
            self.features_data_order.append(stripped_key)
            display_name = self.format_display_name(stripped_key)
            feature_def = {
                "key": stripped_key,
                "displayName": display_name,
                "unit": unit,
                "description": description,
                "tooltip": tooltip,
                "discrete": discrete,
            }
            if discrete:
                self.discrete_features.append(stripped_key)
                column_data = self.get_column_data(key)
                options = self.write_discrete_feature_options(column_data)
                feature_def["options"] = options
            self.feature_defs_data.append(feature_def)


class ImageSettingsDoc:
    """
    Class to store data for the image_settings.json
    """

    def __init__(self):
        self.image_settings_data = {}


class DatasetWriter:
    """
    Class to create the dataset folder and write json files
    """

    def __init__(self, data_loader, inputs):
        self.data = data_loader.data
        self.inputs = inputs

        # initialize the doc classes
        self.cell_feature_doc = CellFeatureDoc()
        self.feature_defs_doc = FeatureDefsDoc(self.data, inputs)
        self.dataset_doc = DatasetDoc(inputs)
        self.image_settings_doc = ImageSettingsDoc()

        # utility variables
        self.features_data_order = self.feature_defs_doc.features_data_order
        self.discrete_features = self.feature_defs_doc.discrete_features
        # dictionary of json file names and their paths
        self.json_file_path_dict = {}

    def get_row_data(self, row):
        """
        Separates the file info and features from the row
        """
        file_info, features = [], []
        for column, value in row.items():
            value = self.cell_feature_doc.convert_str_to_num(value)
            if column in FILEINFO_COLUMN_NAMES:
                file_info.append(value)
            else:
                self.feature_defs_doc.process_features(column, value, features)
        return file_info, features

    def process_data(self):
        """
        Process each row of the csv file and compile the json files
        """
        for row in self.data:
            file_info, features = self.get_row_data(row)
            self.cell_feature_doc.compile_cell_feature_analysis(file_info, features)
        self.feature_defs_doc.compile_feature_defs()
        self.dataset_doc.compile_dataset(self.features_data_order)

    def write_json_files(self, path):
        json_files = {
            CELL_FEATURE_ANALYSIS_FILENAME: self.cell_feature_doc.cell_feature_analysis_data,
            DATASET_FILENAME: self.dataset_doc.dataset_data,
            FEATURE_DEFS_FILENAME: self.feature_defs_doc.feature_defs_data,
            IMAGE_SETTINGS_FILENAME: self.image_settings_doc.image_settings_data,
        }
        for file_name, data in json_files.items():
            file_path = path / file_name
            self.json_file_path_dict[file_name] = file_path
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
        print("Generating JSON files... Done!")

    def create_dataset_folder(self):
        folder_name = f"{self.inputs['dataset_name']}_v{self.inputs['version']}"
        path = Path("data") / folder_name
        path.mkdir(parents=True, exist_ok=True)
        self.write_json_files(path)

    def update_json_file_with_additional_data(self, file_path, additional_data):
        # Load existing data from the JSON file
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}")
            return

        # Update the data with additional settings
        data.update(additional_data)

        # Write the updated data back to the JSON file
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def update_json_files(self, path, additional_data):
        """
        Updates the dataset.json file with additional settings
        """
        self.update_json_file_with_additional_data(path, additional_data)
        print(f"Updating {path}... Done!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the file path: ")

    # Initialize the user input handler, data loader and dataset writer
    input_handler = UserInputHandler(file_path)
    init_inputs = input_handler.inputs
    loader = DataLoader(init_inputs)
    writer = DatasetWriter(loader, init_inputs)

    writer.process_data()
    writer.create_dataset_folder()

    additional_settings = questionary.select(
        "How do you want to add additional settings for the dataset?",
        choices=["By prompts", "Manually edit the JSON files later"],
    ).ask()

    if additional_settings == "By prompts":
        input_handler.dataset_writer = writer
        additional_inputs = input_handler.get_additional_settings()
        dataset_filepath = writer.json_file_path_dict[DATASET_FILENAME]
        writer.update_json_files(dataset_filepath, additional_inputs)
