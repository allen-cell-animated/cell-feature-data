import csv
import sys


class DataLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        """
        Load data from csv file
        """
        with open(self.path, "r") as f:
            reader = csv.reader(f)
            data = list(reader)
        return data


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the file path: ")
    loader = DataLoader(file_path)
    loader.load()
