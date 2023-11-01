import os
import sys
import csv


class DataLoader:
    def __init__(self, path, dataset_name):
        self.path = path
        self.dataset_name = dataset_name
        self.initial_data = None

    def read_csv(self):
        """
        read the csv file and store the data
        """
        try:
            with open(self.path, "r") as f:
                reader = csv.DictReader(f)
                data = list(
                    reader
                )  # data is a list of dictionaries, each dictionary is a row
                self.initial_data = data
                print("CSV file read successfully", self.initial_data)
        except Exception as e:
            print(f"Error while reading CSV: {e}")


class DatasetWriter(DataLoader):
    """
    Class to create the dataset folder and write json files
    """

    def __init__(self, path, dataset_name):
        super().__init__(path, dataset_name)

    def get_inputs(self):
        """
        get the inputs from the user
        """
        # version is required, title and description are optional, default values are set as empty string
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the file path: ")
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    manager = DatasetWriter(file_path, dataset_name)
    manager.read_csv()
