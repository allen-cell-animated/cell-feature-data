import json
import os
import re
import sys
import csv
import pandas as pd
import numpy


class DataLoader:
    FILEINFO_COLUMN_NAMES = [
        "cell_id",
        "parent_id",
        "cell_group",
        "cell_thumbnail",
        "cell_image",
        "parent_thumbnail",
        "parent_image",
    ]

    def __init__(self, path, dataset_name):
        self.path = path
        self.dataset_name = dataset_name
        self.data = self.load_csv()

    def load_csv(self):
        """
        read the csv file and store the data
        """
        try:
            with open(self.path, "r") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error while reading CSV: {e}")
            sys.exit(1)


class DatasetWriter(DataLoader):
    """
    Class to create the dataset folder and write json files
    """

    def __init__(self, path, dataset_name):
        super().__init__(path, dataset_name)
        self.cell_feature_analysis_file = []
        self.feature_defs_file = []
        self.dataset_file = {}
        self.feature_def_keys = []
        self.discrete_features_dict = {}
        self.features_data_order = []

    def get_user_inputs(self):
        self.version = input("Enter the version: ").strip()
        if not self.version or not self.is_valid_version(self.version):
            print("Please enter a valid version in the format [yyyy.number].")
            # recursively call to prompt the user
            return self.get_user_inputs()
        self.title = input("Enter the title: ").strip()
        self.description = input("Enter the description: ").strip()

    def is_valid_version(self, version):
        pattern = r"^\d{4}\.[0-9]+$"
        return re.match(pattern, version) is not None

    def process_data(self):
        for row in self.data:
            file_info, features = self.get_row_data(row)
            self.process_cell_feature_analysis(file_info, features)
        self.process_feature_defs()
        self.process_dataset()

    def get_row_data(self, row):
        file_info = []
        features = []
        for column, value in row.items():
            print(f"{column}: {value}")
            value = self.convert_str_to_num(value)
            if column in self.FILEINFO_COLUMN_NAMES:
                file_info.append(value)
            else:
                if self.is_valid_feature_value(value):
                    features.append(value)
                    self.update_feature_metadata(column, value)
                else:
                    print(f"Invalid value: {value} in column {column}")
                    sys.exit(1)
        return file_info, features

    def get_column_data(self, column):
        column_data = []
        for row in self.data:
            column_data.append(row.get(column, ""))
        return column_data

    def convert_str_to_num(self, value):
        try:
            numeric_value = float(value)
            if numeric_value.is_integer():
                return int(numeric_value)
            return numeric_value
        except ValueError:
            # if not number, return the original value
            return value

    def is_valid_feature_value(self, value):
        return pd.isna(value) or isinstance(value, (int, float))

    def update_feature_metadata(self, column, value):
        is_discrete = self.is_discrete(value)
        self.discrete_features_dict[column] = is_discrete
        if column not in self.feature_def_keys:
            self.feature_def_keys.append(column)

    def is_discrete(self, numeric_value):
        if pd.isna(numeric_value):
            return False
        return numeric_value == int(numeric_value)

    def process_cell_feature_analysis(self, file_info, features):
        self.cell_feature_analysis_file.append(
            {"file_info": file_info, "features": features}
        )

    def process_feature_defs(self):
        description = ""
        tooltip = ""
        discrete = None
        for key in self.feature_def_keys:
            feature_def = {}
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
            self.feature_defs_file.append(feature_def)

    @staticmethod
    def format_display_name(title):
        lowercase_list = ["the", "for", "in", "of", "on", "to", "and", "as", "or"]
        return " ".join(
            word if word in lowercase_list else word.title() for word in title.split()
        )

    @staticmethod
    def get_unit(key):
        match = re.search(r"\((.*?)\)", key)
        if match:
            # get the unit from the key
            unit = match.group(1)
        else:
            unit = ""
        return unit

    def write_discrete_feature_options(self, data_values):
        keys = numpy.unique(data_values)
        options = {}
        # TODO: key in options is optional
        for index, key in enumerate(keys):
            options[key] = {"color": self.get_color(index), "name": key, "key": key}
        return options

    def get_color(self, index):
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

    def process_dataset(self):
        fields_to_write = {
            "title": self.title,
            "version": self.version,
            "name": self.dataset_name,
            "description": self.description,
            "featuresDataOrder": self.features_data_order,
        }
        self.dataset_file.update(fields_to_write)

    def create_dataset_folder(self):
        folder_name = f"{self.dataset_name}_v{self.version}"
        path = os.path.join("data", folder_name)
        os.makedirs(path, exist_ok=True)
        self.write_json_files(path)

    def write_json_files(self, path):
        json_files = {
            "cell_feature_analysis.json": self.cell_feature_analysis_file,
            "feature_defs.json": self.feature_defs_file,
            "dataset.json": self.dataset_file,
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
    writer = DatasetWriter(file_path, dataset_name)
    writer.get_user_inputs()
    writer.process_data()
    writer.create_dataset_folder()
