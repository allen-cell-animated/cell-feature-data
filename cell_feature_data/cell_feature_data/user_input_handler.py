from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging.config
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from cell_feature_data import constants
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


@dataclass
class MegasetDatasetSettings:
    """
    Class to store required dataset settings for megaset
    """

    title: str = ""
    name: str = ""
    dataCreated: str = ""
    publications: List[Dict[str, str]] = field(default_factory=list)
    datasets: list = field(default_factory=list)


@dataclass
class DiscreteFeatureOptions:
    """
    Class to store discrete feature options
    returns a dictionary of color, name, and key as keys
    """

    color: str
    name: str
    key: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeatureDefsSettings:
    """
    Class to store required feature defs settings in feature_defs.json
    """

    key: str
    displayName: str
    unit: str
    description: str = ""
    tooltip: str = ""
    discrete: bool = False
    options: Optional[Dict[str, DiscreteFeatureOptions]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CellFeatureSettings:
    """
    Class to store required cell feature settings
    """

    file_info: List[Union[int, str]]
    features: List[Union[int, float]]

    def to_dict(self) -> Dict[str, List[Union[int, Any]]]:
        return asdict(self)


class DatasetInputHandler:
    """
    Class to handle user inputs for single dataset in dataset.json
    """

    def __init__(
        self, path: str, dataset_writer: Optional[Any] = None, output_path: str = None
    ):
        self.logger = logging.getLogger()
        self.path = Path(path)
        self.dataset_writer = dataset_writer
        self.output_path = Path(output_path) if output_path else Path("data")
        self.inputs = self.get_initial_settings()

    @staticmethod
    def is_valid_version(version: str) -> bool:
        # Check if the version is in the format yyyy.number
        pattern = r"^[0-9]{4}\.[0-9]+$"
        return re.match(pattern, version) is not None

    @staticmethod
    def is_valid_name(name: str) -> bool:
        # Check if the name contains only alphanumeric characters, underscores, and hyphens
        pattern = r"^[a-zA-Z0-9_-]+$"
        return re.match(pattern, name) is not None

    def is_dir_exists(self, name: str) -> bool:
        folder_name = name
        path = self.output_path / folder_name
        return path.exists()

    @staticmethod
    def is_feature_in_list(input: str, features: list) -> bool:
        return input in features

    def get_initial_settings(self) -> DatasetSettings:
        # unsafe_ask() is used to avoid the prompt from being interrupted by the KeyboardInterrupt, which would raise an exception that can be caught
        version = questionary.text(
            "Enter the version(yyyy.number):",
            default=f"{datetime.utcnow().year}.0",
            validate=self.is_valid_version,
        ).unsafe_ask()
        dataset_name = questionary.text(
            "Enter the dataset name:",
            default=self.path.stem.lower().replace(" ", "_"),
            validate=lambda text: (
                True
                if self.is_valid_name(text) and not self.is_dir_exists(text)
                else "Invalid dataset name, should be unique and contain only alphanumeric characters, underscores, and dashes."
            ),
        ).unsafe_ask()
        return DatasetSettings(name=dataset_name, version=version.strip())

    def get_questionary_input(
        self, prompt: str, default=None, validator=None, choices=None
    ) -> Optional[str]:
        """
        Helper function to get user input by prompts with validation and autocompletion
        """
        return (
            questionary.autocomplete(
                prompt,
                default=default,
                validate=validator,
                choices=choices,
            ).unsafe_ask()
            if choices
            else default
        )

    def get_feature(
        self, prompt: str, features: List[str], default_index: int = 0
    ) -> Optional[str]:
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

    def get_additional_settings(self) -> Optional[DatasetSettings]:
        """
        Collect additional settings from the user via interactive prompts
        """
        if not self.dataset_writer:
            self.logger.error("Dataset writer not initialized.")
            return None

        title = questionary.text("Enter the dataset title:").unsafe_ask()
        description = questionary.text("Enter the dataset description:").unsafe_ask()
        thumbnail_root = questionary.text("Enter the thumbnail root:").unsafe_ask()
        download_root = questionary.text("Enter the download root:").unsafe_ask()
        volume_viewer_data_root = questionary.text(
            "Enter the volume viewer data root:"
        ).unsafe_ask()
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


class MegasetInputHandler:
    """
    Class to handle user inputs for megaset in top level dataset.json
    """

    def __init__(self):
        self.inputs = self.get_initial_settings()

    def get_initial_settings(self) -> MegasetDatasetSettings:
        title = questionary.text(
            "Enter the megaset title:",
            validate=lambda text: (
                True if len(text) > 0 else "Megaset title cannot be empty."
            ),
        ).unsafe_ask()
        name = questionary.text(
            "Enter the megaset name:",
            validate=lambda text: (
                True if len(text) > 0 else "Megaset name cannot be empty."
            ),
        ).unsafe_ask()
        return MegasetDatasetSettings(title=title, name=name)

    def collect_publications(self) -> list:
        """
        Collect publication details from the user
        """
        publications = []
        while True:
            title = questionary.text("Enter the publication title:").unsafe_ask()
            url = questionary.text("Enter the publication URL:").unsafe_ask()
            citation = questionary.text("Enter the publication citation:").unsafe_ask()
            publications.append({"title": title, "url": url, "citation": citation})
            add_another = questionary.confirm(
                "Would you like to add another publication?"
            ).unsafe_ask()
            if not add_another:
                break
        return publications

    def get_settings_for_megaset(self) -> Optional[MegasetDatasetSettings]:
        """
        Collect settings for megaset from the user via interactive prompts
        """
        data_created = questionary.text(
            "Enter the date the megaset was created:"
        ).unsafe_ask()

        self.inputs.dataCreated = data_created
        self.inputs.publications = self.collect_publications()

        return self.inputs
