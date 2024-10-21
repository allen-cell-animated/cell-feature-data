import csv
import json
import logging.config
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional
import numpy
import pandas as pd
from cell_feature_data import constants
from cell_feature_data.user_input_handler import (
    DatasetInputHandler,
    MegasetInputHandler,
    DiscreteFeatureOptions,
    FeatureDefsSettings,
    CellFeatureSettings,
)

###############################################################################
log_file_path = Path(__file__).resolve().parent / "logging.conf"
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logger = logging.getLogger()
###############################################################################


class DataLoader:
    """
    Loads the csv file and stores the initial data
    Returns a list of dictionaries, where each dictionary represents a row in the csv file
    """

    def __init__(self, inputs: DatasetInputHandler, path: Path):
        self.inputs = inputs
        self.path = path
        self.data = self.load_csv()

    def load_csv(self) -> List[Dict[str, str]]:
        """
        Read the csv file and store the data
        Returns a list of dictionaries, where each dictionary represents a row in the csv file
        """
        try:
            with open(self.path, "r") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"Error while reading CSV: {e}")
            raise


class MegasetDoc:
    """
    Class to store data for the high-level dataset.json for megasets
    """

    def __init__(self, inputs: MegasetInputHandler):
        self.megaset_data: Dict[str, Any] = asdict(inputs)


class DatasetDoc:
    """
    Class to store data for the dataset.json
    """

    def __init__(self, inputs: DatasetInputHandler):
        self.dataset_data: Dict[str, Any] = asdict(inputs)


class CellFeatureDoc:
    """
    Class to store data for the cell_feature_analysis.json
    """

    def __init__(self):
        self.cell_feature_analysis_data: List[CellFeatureSettings] = []

    @staticmethod
    def convert_str_to_num(value: str) -> Union[int, float, str]:
        try:
            numeric_value = float(value)
            if numeric_value.is_integer():
                return int(numeric_value)
            return numeric_value
        except ValueError:
            # if not number, return the original value
            return value

    def add_cell_feature_analysis(
        self, file_info: List[Union[int, str]], features: List[Union[int, float]]
    ) -> None:
        cell_feature_setting = CellFeatureSettings(file_info, features)
        self.cell_feature_analysis_data.append(cell_feature_setting.to_dict())


class FeatureDefsDoc:
    """
    Class to store data for the feature_defs.json
    """

    def __init__(self, data, inputs):
        self.data = data
        self.inputs = inputs
        self.feature_defs_data: List[FeatureDefsSettings] = []

        # feature names(with units if applicable) in order of appearance in the csv file
        self.feature_def_keys: List[str] = []
        # feature name -> discrete or not
        self.feature_discreteness_map: Dict[str, bool] = {}
        # feature names(without units) in order of appearance in the csv file
        self.features_data_order: List[str] = []
        # list of discrete features
        self.discrete_features: List[str] = []

    @staticmethod
    def is_valid_feature_value(value: Union[int, float]) -> bool:
        return pd.isna(value) or isinstance(value, (int, float))

    @staticmethod
    def is_discrete(numeric_value: Union[int, float]) -> bool:
        """
        Determines if the numeric value is discrete
        """
        return not pd.isna(numeric_value) and numeric_value == int(numeric_value)

    @staticmethod
    def get_unit(key: str) -> str:
        """
        Extracts the unit from the key if present
        """
        match = re.search(r"\((.*?)\)$", key)
        return match.group(1) if match else ""

    @staticmethod
    def format_display_name(title: str) -> str:
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
    def get_color(index: int) -> str:
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

    def update_feature_metadata(self, column: str, value: Union[int, float]) -> None:
        """
        Updates the feature metadata with whether the feature is discrete or not
        Store the list of original feature names for writing the feature defs file
        """
        is_discrete = self.is_discrete(value)
        if (
            column in self.feature_discreteness_map
            and is_discrete != self.feature_discreteness_map[column]
        ):
            logger.warning(
                f"Column {column} has both discrete and continuous values. Please make sure that all values in a column are either discrete or continuous."
            )
            return
        self.feature_discreteness_map[column] = is_discrete
        if column not in self.feature_def_keys:
            self.feature_def_keys.append(column)

    def process_features(
        self, column: str, value: Union[int, float], features: List[Union[int, float]]
    ) -> None:
        if self.is_valid_feature_value(value):
            features.append(value)
            self.update_feature_metadata(column, value)
        else:
            logger.error(f"Invalid value: {value} in column {column}")
            raise ValueError

    def get_column_data(self, column: str) -> List[str]:
        """
        Returns the column data from the dataset
        """
        column_data = []
        for row in self.data:
            column_data.append(row.get(column, ""))
        return column_data

    def write_discrete_feature_options(
        self, data_values: List[str]
    ) -> Optional[Dict[str, DiscreteFeatureOptions]]:
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
            options[key] = DiscreteFeatureOptions(
                color=self.get_color(index), name=key, key=key
            )
        return options

    def add_feature_defs(self) -> None:
        for key in self.feature_def_keys:
            discrete = self.feature_discreteness_map[key]
            unit = self.get_unit(key)
            stripped_key = key.replace(f"({unit})", "").strip()
            self.features_data_order.append(stripped_key)
            display_name = self.format_display_name(stripped_key)
            feature_def = FeatureDefsSettings(
                key=stripped_key,
                displayName=display_name,
                unit=unit,
                discrete=discrete,
            )
            if discrete:
                self.discrete_features.append(stripped_key)
                column_data = self.get_column_data(key)
                options = self.write_discrete_feature_options(column_data)
                feature_def.options = options
            self.feature_defs_data.append(feature_def.to_dict())


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

    def __init__(
        self,
        inputs: Union[DatasetInputHandler, MegasetInputHandler],
        data_loader: Optional[DataLoader] = None,
        for_megaset: bool = False,
    ):
        self.inputs = inputs
        if data_loader:
            self.data = data_loader.data

            # initialize the doc classes
            self.cell_feature_doc = CellFeatureDoc()
            self.feature_defs_doc = FeatureDefsDoc(self.data, inputs)
            self.dataset_doc = DatasetDoc(inputs)
            self.image_settings_doc = ImageSettingsDoc()

            # utility variables
            self.features_data_order: List[str] = (
                self.feature_defs_doc.features_data_order
            )
            self.discrete_features: List[str] = self.feature_defs_doc.discrete_features
        self.for_megaset = for_megaset
        self.mega_dataset_doc = MegasetDoc(inputs)
        # dictionary of json file names and their paths
        self.json_file_path_dict: Dict[str, Path] = {}
        # list of updated dataset names in the dataset.json, used for updating additional settings when updating a megaset
        self.updated_dataset_list: List[str] = []

    def get_row_data(
        self, row: Dict[str, str]
    ) -> Tuple[List[Union[int, str]], List[Union[int, float]]]:
        """
        Separates the file info and features from the row
        """
        file_info, features = [], []
        for column, value in row.items():
            value = self.cell_feature_doc.convert_str_to_num(value)
            if column in constants.FILEINFO_COLUMN_NAMES:
                file_info.append(value)
            else:
                self.feature_defs_doc.process_features(column, value, features)
        return file_info, features

    def process_data(self) -> None:
        """
        Process each row of the csv file and create cell feature analysis and feature defs
        """
        for row in self.data:
            file_info, features = self.get_row_data(row)
            self.cell_feature_doc.add_cell_feature_analysis(file_info, features)
        self.feature_defs_doc.add_feature_defs()

    def write_json_files(self, path: Path, write_megaset: bool = False) -> None:
        if write_megaset:
            json_files = {
                constants.MEGASET_DATASET_FILENAME: self.mega_dataset_doc.megaset_data,
            }
        else:
            json_files = {
                constants.CELL_FEATURE_ANALYSIS_FILENAME: self.cell_feature_doc.cell_feature_analysis_data,
                constants.DATASET_FILENAME: self.dataset_doc.dataset_data,
                constants.FEATURE_DEFS_FILENAME: self.feature_defs_doc.feature_defs_data,
                constants.IMAGE_SETTINGS_FILENAME: self.image_settings_doc.image_settings_data,
            }
        for file_name, data in json_files.items():
            file_path = path / file_name
            self.json_file_path_dict[file_name] = file_path
            if not file_path.exists():
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=4)
            else:
                logger.info(
                    f"Skip writing {file_name} as it already exists at {file_path}, please edit the json file if needed."
                )

    def create_dataset_folder(self, output_path: str) -> None:
        if self.for_megaset:
            folder_name = self.inputs.name
        else:
            folder_name = f"{self.inputs.name}_v{self.inputs.version}"
        path = Path(output_path) / folder_name
        path.mkdir(parents=True, exist_ok=True)
        self.write_json_files(path)
        logger.info(f"Successfully created {folder_name} at {path}.")

        # If creating within a megaset, update the top-level dataset.json
        dataset_json_path = Path(output_path) / constants.MEGASET_DATASET_FILENAME
        if dataset_json_path.exists():
            new_dataset_entry = folder_name
            self.update_dataset_json(
                Path(output_path) / constants.MEGASET_DATASET_FILENAME,
                new_dataset_entry,
            )

    def update_json_file_with_additional_data(
        self, file_path: Path, additional_data: Dict[str, Any]
    ) -> None:
        """
        Updates the JSON file with additional settings
        """
        # Load existing data from the JSON file
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {file_path}")
            raise

        # Update the data with additional settings
        data.update(additional_data)

        # Write the updated data back to the JSON file
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        logger.info(f"Successfully updated {file_path} with additional settings.")

    def update_dataset_json(self, file_path: Path, new_dataset: str) -> None:
        """
        Updates the top-level dataset.json file with the new dataset
        """
        try:
            with open(file_path, "r+") as file:
                data = json.load(file)
                data["datasets"].append(new_dataset)
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                self.updated_dataset_list = data["datasets"]

            logger.info(
                f"Successfully updated {file_path} with the new dataset: {new_dataset}."
            )

        except KeyError:
            logger.error(
                f"Key 'datasets' not found in {file_path}, please check the JSON file."
            )
            raise
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {file_path}")
            raise
