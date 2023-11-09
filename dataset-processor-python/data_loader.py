import json
import os
import re
import sys
import csv
import pandas as pd


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
        self.initial_data = self.read_csv()

    def read_csv(self):
        """
        read the csv file and store the data
        """
        print("Reading the CSV file...")
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

    def get_inputs(self):
        """
        get the inputs from the user
        """
        # TODO: clarify the version format, input validation needed
        self.version = input("Enter the version in the format: ").strip()
        if not self.version:
            print("Please enter a valid version.")
            # recursively call to prompt the user
            return self.get_inputs()
        else:
            self.title = input("Enter the title: ").strip()
            self.description = input("Enter the description: ").strip()

    def sort_data(self):
        for row in self.initial_data:
            file_info = []
            features = []
            for column, value in row.items():
                if column in self.FILEINFO_COLUMN_NAMES:
                    value = self._convert_str_to_num(value)
                    file_info.append(value)
                else:
                    value = self._convert_str_to_num(value)
                    if (
                        pd.isna(value)
                        or isinstance(value, int)
                        or isinstance(value, float)
                    ):
                        features.append(value)
                        is_discrete = self._is_discrete(value)
                        self.discrete_features_dict[column] = is_discrete
                        if column not in self.feature_def_keys:
                            self.feature_def_keys.append(column)
                    else:
                        print(f"Invalid value: {value} in column {column}")
                        sys.exit(1)
            self.prepare_cell_feature_analysis(file_info, features)
        self.prepare_feature_defs()
        self.prepare_dataset()

    def _is_discrete(self, numeric_value):
        if pd.isna(numeric_value):
            return False
        return numeric_value == int(numeric_value)

    def _convert_str_to_num(self, value):
        try:
            numeric_value = float(value)
            if numeric_value.is_integer():
                return int(numeric_value)
            return numeric_value
        except ValueError:
            # return the original value
            return value

    def prepare_cell_feature_analysis(self, file_info, features):
        self.cell_feature_analysis_file.append(
            {"file_info": file_info, "features": features}
        )

    @staticmethod
    def _title_except_small_words(title):
        lowercase_list = ["the", "for", "in", "of", "on", "to", "and", "as", "or"]
        return " ".join(
            [word if word in lowercase_list else word.title() for word in title.split()]
        )

    def _has_unit(self, key):
        has_unit = re.search(r"\((.*?)\)", key)
        if has_unit:
            # get the unit from the key
            unit = has_unit.group(1)
        else:
            unit = ""
        return unit

    def prepare_feature_defs(self):
        description = ""
        tooltip = ""
        discrete = None
        for key in self.feature_def_keys:
            discrete = self.discrete_features_dict[key]
            unit = self._has_unit(key)
            key = key.replace(f"({unit})", "").strip()
            self.features_data_order.append(key)
            display_name = DatasetWriter._title_except_small_words(
                key.replace("-", " ")
            )
            self.feature_defs_file.append(
                {
                    "key": key,
                    "displayName": display_name,
                    "unit": unit,
                    "description": description,
                    "tooltip": tooltip,
                    "discrete": discrete,
                }
            )

    def prepare_dataset(self):
        # TODO: get more input data from users
        fields_to_write = {
            "version": self.version,
            "title": self.title,
            "description": self.description,
            "featuresDataOrder": self.features_data_order,
        }
        self.dataset_file.update(fields_to_write)
        return self.dataset_file

    def create_dataset(self):
        """
        create a folder with the database_name
        initialize the folder with required json files
        """
        print("Creating the dataset folder...")
        # TODO: clarify the folder name and dataset name
        folder_name = f"dataset-{self.dataset_name}-v{self.version}"
        path = os.path.join("data", folder_name)
        os.makedirs(path, exist_ok=True)
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
    writer.get_inputs()
    writer.sort_data()
    writer.create_dataset()
