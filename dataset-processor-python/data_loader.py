import os
import sys
import csv
import json


class DataLoader:
    def __init__(self, path, dataset_name):
        self.path = path
        self.dataset_name = dataset_name

    def csv_to_json(self):
        """
        converts the csv file to json format
        """
        try:
            with open(self.path, "r") as f:
                reader = csv.DictReader(f)
                data = list(reader)
            json_filename = self.dataset_name + ".json"
            full_path = os.path.join(os.path.dirname(self.path), json_filename)
            with open(full_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error while converting CSV to JSON: {e}")


class DatasetManager(DataLoader):
    """
    Class to create the dataset folder and json files
    """

    def __init__(self, path, dataset_name):
        super().__init__(path, dataset_name)

    def get_inputs(self):
        """
        get the inputs from the user
        """
        # version is required, title and description are optional
        # Q: should we have a default title and description?
        # return version, title, description
        pass

    def create_dataset_folder(self):
        """
        create a folder with the database_name
        initialize the folder with required json files
        """
        # folder_name = self.dataset_name + "_" + version
        # path = os.path.join("data", folder_name)
        # os.makedirs(path, exist_ok=True)
        # create json files -> feature_defs.json, dataset.json, cell_feature_analysis.json, image_settings.json
        pass


class FeatureDefsHandler:
    """
    Handles operations on feature_defs.json
    """

    def __init__(self) -> None:
        pass


class DatasetHandler:
    """
    Handles operations on dataset.json
    """

    def __init__(self) -> None:
        pass


class CellFeatureAnalysisHandler:
    """
    Handles operations on cell_feature_analysis.json(aka features.json)
    """

    def __init__(self) -> None:
        pass


class ImageSettingsHandler:
    """
    Handles operations on image_settings.json(aka images.json)
    """

    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the file path: ")
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    manager = DatasetManager(file_path, dataset_name)
    manager.csv_to_json()
