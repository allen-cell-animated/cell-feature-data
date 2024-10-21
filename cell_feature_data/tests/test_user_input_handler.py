import pytest
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Dict, List

from cell_feature_data import constants
from cell_feature_data.user_input_handler import (
    DatasetInputHandler,
    MegasetInputHandler,
)


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


@pytest.fixture
def dataset_input_handler():
    with patch.object(
        DatasetInputHandler, "get_initial_settings"
    ) as mock_get_initial_settings:
        mock_get_initial_settings.return_value = DatasetSettings(
            name="test_dataset", version="2024.1"
        )
        return DatasetInputHandler(path="test_path")


@pytest.fixture
def megaset_input_handler():
    with patch.object(
        MegasetInputHandler, "get_initial_settings"
    ) as mock_get_initial_settings:
        mock_get_initial_settings.return_value = MegasetDatasetSettings(
            title="Test Megaset", name="test_megaset"
        )
        return MegasetInputHandler()


@patch("cell_feature_data.user_input_handler.questionary.text")
def test_get_initial_settings(mock_questionary_text, dataset_input_handler):
    mock_questionary_text.side_effect = [
        MagicMock(unsafe_ask=lambda: "2024.1"),
        MagicMock(unsafe_ask=lambda: "test_dataset"),
    ]

    settings = dataset_input_handler.get_initial_settings()

    assert settings.name == "test_dataset"
    assert settings.version == "2024.1"


def test_is_valid_version(dataset_input_handler):
    assert dataset_input_handler.is_valid_version("2023.1")
    assert not dataset_input_handler.is_valid_version("23.1")
    assert not dataset_input_handler.is_valid_version("2023-1")


def test_is_valid_name(dataset_input_handler):
    assert dataset_input_handler.is_valid_name("valid_name-123")
    assert not dataset_input_handler.is_valid_name("invalid name!")
    assert not dataset_input_handler.is_valid_name("invalid/name")


@patch("cell_feature_data.user_input_handler.Path.exists")
def test_is_dir_exists(mock_path_exists, dataset_input_handler):
    mock_path_exists.return_value = True
    assert dataset_input_handler.is_dir_exists("existing_dir")

    mock_path_exists.return_value = False
    assert not dataset_input_handler.is_dir_exists("non_existing_dir")


def test_is_feature_in_list(dataset_input_handler):
    features = ["feature1", "feature2", "feature3"]
    assert dataset_input_handler.is_feature_in_list("feature1", features)
    assert not dataset_input_handler.is_feature_in_list("feature4", features)


@patch("cell_feature_data.user_input_handler.questionary.autocomplete")
def test_get_questionary_input(mock_questionary_autocomplete, dataset_input_handler):
    mock_questionary_autocomplete.return_value.unsafe_ask.return_value = (
        "selected_feature"
    )
    feature = dataset_input_handler.get_questionary_input(
        "Select a feature:",
        default="feature1",
        validator=lambda x: True,
        choices=["feature1", "feature2"],
    )
    assert feature == "selected_feature"


@patch("cell_feature_data.user_input_handler.questionary.text")
def test_get_additional_settings(mock_questionary_text, dataset_input_handler):
    dataset_input_handler.dataset_writer = MagicMock()
    dataset_input_handler.dataset_writer.features_data_order = ["feature1", "feature2"]
    dataset_input_handler.dataset_writer.discrete_features = ["discrete1", "discrete2"]
    mock_questionary_text.side_effect = [
        MagicMock(unsafe_ask=lambda: "Title"),
        MagicMock(unsafe_ask=lambda: "Description"),
        MagicMock(unsafe_ask=lambda: "ThumbnailRoot"),
        MagicMock(unsafe_ask=lambda: "DownloadRoot"),
        MagicMock(unsafe_ask=lambda: "VolumeViewerDataRoot"),
    ]

    with patch.object(
        dataset_input_handler,
        "get_feature",
        side_effect=["xAxis", "yAxis", "colorBy", "groupBy"],
    ):
        settings = dataset_input_handler.get_additional_settings()

        assert settings.title == "Title"
        assert settings.description == "Description"
        assert settings.thumbnailRoot == "ThumbnailRoot"
        assert settings.downloadRoot == "DownloadRoot"
        assert settings.volumeViewerDataRoot == "VolumeViewerDataRoot"
        assert settings.xAxis["default"] == "xAxis"
        assert settings.yAxis["default"] == "yAxis"
        assert settings.colorBy["default"] == "colorBy"
        assert settings.groupBy["default"] == "groupBy"


@patch("cell_feature_data.user_input_handler.questionary.text")
def test_get_initial_megasettings(mock_questionary_text, megaset_input_handler):
    mock_questionary_text.side_effect = [
        MagicMock(unsafe_ask=lambda: "Test Megaset Title"),
        MagicMock(unsafe_ask=lambda: "test_megaset_name"),
    ]

    settings = megaset_input_handler.get_initial_settings()

    assert settings.title == "Test Megaset Title"
    assert settings.name == "test_megaset_name"


@patch("cell_feature_data.user_input_handler.questionary.text")
@patch("cell_feature_data.user_input_handler.questionary.confirm")
def test_collect_publications(
    mock_questionary_confirm, mock_questionary_text, megaset_input_handler
):
    mock_questionary_text.side_effect = [
        MagicMock(unsafe_ask=lambda: "Publication Title 1"),
        MagicMock(unsafe_ask=lambda: "http://publication1.url"),
        MagicMock(unsafe_ask=lambda: "Citation 1"),
        MagicMock(unsafe_ask=lambda: "Publication Title 2"),
        MagicMock(unsafe_ask=lambda: "http://publication2.url"),
        MagicMock(unsafe_ask=lambda: "Citation 2"),
    ]
    mock_questionary_confirm.side_effect = [
        MagicMock(unsafe_ask=lambda: True),
        MagicMock(unsafe_ask=lambda: False),
    ]

    publications = megaset_input_handler.collect_publications()

    assert len(publications) == 2
    assert publications[0]["title"] == "Publication Title 1"
    assert publications[0]["url"] == "http://publication1.url"
    assert publications[0]["citation"] == "Citation 1"
    assert publications[1]["title"] == "Publication Title 2"
    assert publications[1]["url"] == "http://publication2.url"
    assert publications[1]["citation"] == "Citation 2"


@patch("cell_feature_data.user_input_handler.questionary.text")
@patch("cell_feature_data.user_input_handler.questionary.confirm")
def test_get_settings_for_megaset(
    mock_questionary_confirm, mock_questionary_text, megaset_input_handler
):
    mock_questionary_text.side_effect = [
        MagicMock(unsafe_ask=lambda: "2024-08-06"),
        MagicMock(unsafe_ask=lambda: "Publication Title 1"),
        MagicMock(unsafe_ask=lambda: "http://publication1.url"),
        MagicMock(unsafe_ask=lambda: "Citation 1"),
        MagicMock(unsafe_ask=lambda: "Publication Title 2"),
        MagicMock(unsafe_ask=lambda: "http://publication2.url"),
        MagicMock(unsafe_ask=lambda: "Citation 2"),
    ]
    mock_questionary_confirm.side_effect = [
        MagicMock(unsafe_ask=lambda: True),
        MagicMock(unsafe_ask=lambda: False),
    ]

    settings = megaset_input_handler.get_settings_for_megaset()

    assert settings.dataCreated == "2024-08-06"
    assert len(settings.publications) == 2
    assert settings.publications[0]["title"] == "Publication Title 1"
    assert settings.publications[0]["url"] == "http://publication1.url"
    assert settings.publications[0]["citation"] == "Citation 1"
    assert settings.publications[1]["title"] == "Publication Title 2"
    assert settings.publications[1]["url"] == "http://publication2.url"
    assert settings.publications[1]["citation"] == "Citation 2"
