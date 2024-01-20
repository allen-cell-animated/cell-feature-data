from dataclasses import dataclass, field
import logging.config
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional
import constants
import questionary
import re


@dataclass
class DatasetSettings:
    """
    Class to store required dataset settings
    """

    title: str = ""
    version: str = ""
    name: str = ""
    image: str = ""
    description: str = ""
    featureDefsPath: str = constants.FEATURE_DEFS_FILENAME
    featuresDataPath: str = constants.CELL_FEATURE_ANALYSIS_FILENAME
    viewerSettingsPath: str = constants.IMAGE_SETTINGS_FILENAME
    albumPath: str = ""
    thumbnailRoot: str = ""
    downloadRoot: str = ""
    volumeViewerDataRoot: str = ""
    xAxis: Dict[str, str] = field(default_factory=dict)
    yAxis: Dict[str, str] = field(default_factory=dict)
    colorBy: Dict[str, str] = field(default_factory=dict)
    groupBy: Dict[str, str] = field(default_factory=dict)
    featuresDisplayOrder: list = field(default_factory=list)
    featuresDataOrder: list = field(default_factory=list)


class UserInputHandler:
    """
    Class to handle user inputs
    """

    def __init__(self, path: str, dataset_writer: Optional[Any] = None):
        # Configure logger
        logging.config.fileConfig(Path(__file__).resolve().parent / "logging.conf")
        self.logger = logging.getLogger()

        self.path = Path(path)
        self.dataset_writer = dataset_writer
        self.inputs = self.get_initial_settings()

    @staticmethod
    def is_valid_version(version: str) -> bool:
        pattern = r"^[0-9]{4}\.[0-9]+$"
        return re.match(pattern, version) is not None

    @staticmethod
    def is_feature_in_list(input: str, features: list) -> bool:
        return input in features

    def get_initial_settings(self):
        version = questionary.text(
            "Enter the version(yyyy.number):",
            default="2024.0",
            validate=self.is_valid_version,
        ).ask()
        dataset_name = self.path.stem.lower().replace(" ", "_")
        return DatasetSettings(name=dataset_name, version=version.strip())

    def get_questionary_input(
        self, prompt: str, default=None, validator=None, choices=None
    ):
        """
        Helper function to get user input by prompts with validation and autocompletion
        """
        return (
            questionary.autocomplete(
                prompt,
                default=default,
                validate=validator,
                choices=choices,
            ).ask()
            if choices
            else default
        )

    def get_feature(self, prompt: str, features: List[str], default_index: int = 0) -> str:
        """
        Get feature input from the user
        """
        if not features or default_index >= len(features) or default_index < 0:
            self.logger.error("Invalid feature list or default index.")
            return None
        default_feature = features[default_index]

        return self.get_questionary_input(
            prompt,
            default=default_feature,
            choices=features,
            validator=lambda user_input: self.is_feature_in_list(user_input, features),
        )

    def get_additional_settings(self):
        """
        Collect additional settings from the user via interactive prompts
        """
        if not self.dataset_writer:
            self.logger.error("Dataset writer not initialized.")
            return None

        title = questionary.text("Enter the dataset title:").ask()
        description = questionary.text("Enter the dataset description:").ask()
        thumbnail_root = questionary.text("Enter the thumbnail root:").ask()
        download_root = questionary.text("Enter the download root:").ask()
        volume_viewer_data_root = questionary.text(
            "Enter the volume viewer data root:"
        ).ask()
        cell_features = self.dataset_writer.features_data_order
        discrete_features = self.dataset_writer.discrete_features
        xAxis_default = self.get_feature(
            "Enter the feature name for xAxis default:", cell_features
        )
        yAxis_default = self.get_feature(
            "Enter the feature name for yAxis default:", cell_features, default_index=1
        )
        color_by = self.get_feature(
            "Enter the feature name for colorBy:", cell_features
        )
        group_by = self.get_feature(
            "Enter the feature name for groupBy:", discrete_features
        )

        self.inputs.title = title
        self.inputs.description = description
        self.inputs.thumbnailRoot = thumbnail_root
        self.inputs.downloadRoot = download_root
        self.inputs.volumeViewerDataRoot = volume_viewer_data_root
        self.inputs.xAxis = {"default": xAxis_default, "exclude": []}
        self.inputs.yAxis = {"default": yAxis_default, "exclude": []}
        self.inputs.colorBy = {"default": color_by}
        self.inputs.groupBy = {"default": group_by}
        self.inputs.featuresDataOrder = cell_features

        return self.inputs
