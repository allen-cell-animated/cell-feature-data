import json
import os
import re
import sys
import csv
import pandas as pd
import numpy


class UserInputHandler:
    """
    Class to handle user inputs
    """

    def __init__(self, path, dataset_name):
        self.path = path
        self.dataset_name = dataset_name
        self.inputs = self.get_user_inputs()

    @staticmethod
    def is_valid_version(version):
        pattern = r"^\d{4}\.[0-9]+$"
        return re.match(pattern, version) is not None

    def get_user_inputs(self):
        version = input("Enter the version: ").strip()
        if not version or not self.is_valid_version(version):
            print("Please enter a valid version in the format [yyyy.number].")
            return self.get_user_inputs()
        title = input("Enter the title: ").strip()
        description = input("Enter the description: ").strip()
        return {
            "path": self.path,
            "dataset_name": self.dataset_name,
            "version": version,
            "title": title,
            "description": description,
        }


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
        """
        try:
            with open(self.inputs["path"], "r") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error while reading CSV: {e}")
            return None


class DatasetWriter:
    """
    Class to create the dataset folder and write json files
    """

    FILEINFO_COLUMN_NAMES = [
        "cell_id",
        "parent_id",
        "cell_group",
        "cell_thumbnail",
        "cell_image",
        "parent_thumbnail",
        "parent_image",
    ]

    def __init__(self, data_loader, inputs):
        # initialize the json files in the data folder
        self.data = data_loader.data
        self.inputs = inputs
        self.cell_feature_analysis_data = []
        self.feature_defs_data = []
        self.dataset_data = {}
        # utility variables - to organize and categorize the feature data for file writing
        self.feature_def_keys = set()
        self.discrete_features_dict = {}
        self.features_data_order = []

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

    @staticmethod
    def is_valid_feature_value(value):
        return pd.isna(value) or isinstance(value, (int, float))

    @staticmethod
    def is_discrete(numeric_value):
        """
        Determines if the numeric value is discrete
        """
        return not pd.isna(numeric_value) and numeric_value == int(numeric_value)

    def update_feature_metadata(self, column, value):
        is_discrete = self.is_discrete(value)
        if (
            column in self.discrete_features_dict
            and is_discrete != self.discrete_features_dict[column]
        ):
            print(
                f"Column {column} has both discrete and continuous values. Please make sure that all values in a column are either discrete or continuous."
            )
            return
        self.discrete_features_dict[column] = is_discrete
        self.feature_def_keys.add(column)

    def process_features(self, column, value, features):
        if self.is_valid_feature_value(value):
            features.append(value)
            self.update_feature_metadata(column, value)
        else:
            print(f"Invalid value: {value} in column {column}")
            return

    @staticmethod
    def get_unit(key):
        """
        Extracts the unit from the key if present
        """
        match = re.search(r"\((.*?)\)", key)
        return match.group(1) if match else ""

    @staticmethod
    def format_display_name(title):
        """
        Formats the title to display name, e.g. "the title of the feature" -> "The Title of the Feature"
        """
        lowercase_list = ["the", "for", "in", "of", "on", "to", "and", "as", "or"]
        title_words = title.split()
        return " ".join(
            word if (word in lowercase_list and i != 0) else word.title()
            for i, word in enumerate(title_words)
        )

    def get_column_data(self, column):
        """
        Returns the column data from the dataset
        """
        column_data = []
        for row in self.data:
            column_data.append(row.get(column, ""))
        return column_data

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

    def write_discrete_feature_options(self, data_values):
        keys = numpy.unique(data_values)
        options = {}
        for index, key in enumerate(keys):
            # In options, "color" and "name" are required, and "key" is optional. "name" and "key" should be defined by the user.
            options[key] = {"color": self.get_color(index), "name": "", "key": ""}
        return options

    def compile_feature_defs(self):
        description = ""
        tooltip = ""
        for key in self.feature_def_keys:
            discrete = self.discrete_features_dict[key]
            unit = self.get_unit(key)
            stripped_key = key.replace(f"({unit})", "").strip()
            self.features_data_order.append(stripped_key)
            display_name = DatasetWriter.format_display_name(
                stripped_key.replace("-", " ")
            )
            feature_def = {
                "key": stripped_key,
                "displayName": display_name,
                "unit": unit,
                "description": description,
                "tooltip": tooltip,
                "discrete": discrete,
            }
            if discrete:
                column_data = self.get_column_data(key)
                options = self.write_discrete_feature_options(column_data)
                feature_def["options"] = options
            self.feature_defs_data.append(feature_def)

    def compile_dataset(self):
        fields_to_write = {
            "title": self.inputs["title"],
            "version": self.inputs["version"],
            "name": self.inputs["dataset_name"],
            "description": self.inputs["description"],
            "featureDefsPath": "feature_defs.json",
            "featuresDataPath": "cell_feature_analysis.json",
            "viewerSettingsPath": "image_settings.json",
            "featuresDataOrder": self.features_data_order,
        }
        self.dataset_data.update(fields_to_write)

    def get_row_data(self, row):
        """
        Separates the file info and features from the row
        """
        file_info, features = [], []
        for column, value in row.items():
            value = self.convert_str_to_num(value)
            if column in self.FILEINFO_COLUMN_NAMES:
                file_info.append(value)
            else:
                self.process_features(column, value, features)
        return file_info, features

    def compile_cell_feature_analysis(self, file_info, features):
        self.cell_feature_analysis_data.append(
            {"file_info": file_info, "features": features}
        )

    def process_data(self):
        """
        Process each row of the csv file and compile the json files
        """
        for row in self.data:
            file_info, features = self.get_row_data(row)
            self.compile_cell_feature_analysis(file_info, features)
        self.compile_feature_defs()
        self.compile_dataset()

    def create_dataset_folder(self):
        folder_name = f"{self.inputs['dataset_name']}_v{self.inputs['version']}"
        path = os.path.join("data", folder_name)
        os.makedirs(path, exist_ok=True)
        self.write_json_files(path)

    def write_json_files(self, path):
        json_files = {
            "cell_feature_analysis.json": self.cell_feature_analysis_data,
            "feature_defs.json": self.feature_defs_data,
            "dataset.json": self.dataset_data,
            "image_settings.json": {},
        }
        for file_name, data in json_files.items():
            file_path = os.path.join(path, file_name)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the file path: ")
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    input_handler = UserInputHandler(file_path, dataset_name)
    inputs = input_handler.inputs
    if not inputs:
        print("Please enter valid inputs.")
        sys.exit(1)
    loader = DataLoader(inputs)
    writer = DatasetWriter(loader, inputs)
    writer.process_data()
    writer.create_dataset_folder()
