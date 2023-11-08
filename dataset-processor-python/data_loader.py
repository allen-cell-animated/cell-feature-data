import json
import os
import re
import sys
import csv


class DataLoader:
    def __init__(self, path, dataset_name):
        self.path = path
        self.dataset_name = dataset_name
        self.initial_data = None
        self.feature_def_keys = None

    # TODO: how to separate the test data columns efficiently? looking for specific keys?

    def read_csv(self):
        """
        read the csv file and store the data
        """
        try:
            print("Reading the CSV file...")
            with open(self.path, "r") as f:
                reader = csv.DictReader(f)
                data = list(reader)
                self.initial_data = data
                self.feature_def_keys = reader.fieldnames  # TODO: titles in column H-K
        except Exception as e:
            print(f"Error while reading CSV: {e}")


class DatasetWriter(DataLoader):
    """
    Class to create the dataset folder and write json files
    """

    def __init__(self, path, dataset_name):
        super().__init__(path, dataset_name)
        self.version = None
        self.title = ""
        self.description = ""

    def get_inputs(self):
        """
        get the inputs from the user
        """
        # TODO: clarify the version format
        self.version = input("Enter the version in the format(yyyy.version): ").strip()
        if not self.version:
            print("Please enter a valid version.")
            # recursively call to prompt the user
            return self.get_inputs()
        else:
            self.title = input("Enter the title: ").strip()
            self.description = input("Enter the description: ").strip()

    def prepare_cell_feature_analysis(self):
        cell_feature_analysis_file = []
        for row in self.initial_data:
            file_info = []
            features = []
            print("Row:", row)
            for column, value in row.items():
                print(f"Column: {column}, Value: {value}")
                file_info.append(value)  # TODO: value in column A-G
                features.append(value)  # TODO: in column H-K
            cell_feature_analysis_file.append(
                {"file_info": file_info, "features": features}
            )
        return cell_feature_analysis_file

    def _title_except_small_words(title):
        lowercase_list = ["the", "for", "in", "of", "on", "to", "and", "as", "or"]
        return " ".join(
            [word if word in lowercase_list else word.title() for word in title.split()]
        )

    def prepare_feature_defs(self):
        feature_defs_file = []
        description = ""
        unit = ""
        tooltip = ""
        discrete = None
        for key in self.feature_def_keys:
            has_unit = re.search(r"\((.*?)\)", key)
            if has_unit:
                # get the unit from the key
                unit = has_unit.group(1)
                # remove the unit from the key
                key = key.replace(f"({unit})", "").strip()
            display_name = DatasetWriter._title_except_small_words(key.replace("-", " "))
            feature_defs_file.append(
                {
                    "key": key,
                    "displayName": display_name,
                    "unit": unit,
                    "description": description,
                    "tooltip": tooltip,
                    "discrete": discrete,
                }
            )
        return feature_defs_file

    def create_dataset(self):
        """
        create a folder with the database_name
        initialize the folder with required json files
        """
        print("Creating the dataset folder...")
        # TODO: clarify the folder name
        folder_name = f"dataset-{self.dataset_name}-v{self.version}"
        path = os.path.join("data", folder_name)
        os.makedirs(path, exist_ok=True)
        print("Creating the json files...")
        json_files = {
            "feature_defs.json": self.prepare_feature_defs(),
            "dataset.json": {},
            "cell_feature_analysis.json": self.prepare_cell_feature_analysis(),
            "image_settings.json": {},
        }

        # write the json files with the default values
        for file_name, data in json_files.items():
            with open(os.path.join(path, file_name), "w") as f:
                if isinstance(data, str):
                    f.write(data)
                else:
                    json.dump(data, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the file path: ")
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    manager = DatasetWriter(file_path, dataset_name)
    manager.read_csv()
    manager.get_inputs()
    manager.create_dataset()
