import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
from cell_feature_data.user_input_handler import DatasetInputHandler
from cell_feature_data.data_loader import (
    CellFeatureDoc,
    DataLoader,
    DatasetWriter,
    FeatureDefsDoc,
)

test_csv_file_path = Path(
    "cell_feature_data/tests/test_data/single_dataset_test_data.csv"
)


@patch("questionary.text")
def test_dataloader_csv_reading_error_handling(mock_questionary_text):
    mock_questionary_text.return_value.unsafe_ask.return_value = "mocked_input"

    handler = DatasetInputHandler(path="dummy_path", output_path="dummy_output_path")
    inputs = handler.inputs

    data_loader = DataLoader(inputs, test_csv_file_path)

    assert len(data_loader.data) > 0
    assert isinstance(data_loader.data, list)
    assert isinstance(data_loader.data[0], dict)


def test_convert_str_to_num():
    assert CellFeatureDoc.convert_str_to_num("10") == 10
    assert CellFeatureDoc.convert_str_to_num("10.5") == 10.5
    assert CellFeatureDoc.convert_str_to_num("not_a_number") == "not_a_number"


def test_add_cell_feature_analysis():
    cell_feature_doc = CellFeatureDoc()
    file_info = [1, 2, "file_name"]
    features = [4.5, 5.5, 6.5]

    with patch(
        "cell_feature_data.data_loader.CellFeatureSettings.to_dict",
        return_value={"file_info": file_info, "features": features},
    ):
        cell_feature_doc.add_cell_feature_analysis(file_info, features)

    assert len(cell_feature_doc.cell_feature_analysis_data) == 1
    assert cell_feature_doc.cell_feature_analysis_data[0] == {
        "file_info": file_info,
        "features": features,
    }


def test_is_valid_feature_value():
    assert FeatureDefsDoc.is_valid_feature_value(10)
    assert FeatureDefsDoc.is_valid_feature_value(10.5)
    assert FeatureDefsDoc.is_valid_feature_value(np.nan)
    assert not FeatureDefsDoc.is_valid_feature_value("not_a_number")


def test_get_unit():
    assert (
        FeatureDefsDoc.get_unit("cell-surface-area (\u00b5m\u00b2)") == "\u00b5m\u00b2"
    )
    assert FeatureDefsDoc.get_unit("cellular-volume (fL)") == "fL"
    assert not FeatureDefsDoc.get_unit("cell-line")


def test_format_display_name():
    assert (
        FeatureDefsDoc.format_display_name("interphase-or-mitosis")
        == "Interphase or Mitosis"
    )
    assert (
        not FeatureDefsDoc.format_display_name("interphase-or-mitosis")
        == "Interphase Or Mitosis"
    )
    assert FeatureDefsDoc.format_display_name("cellular-volume") == "Cellular Volume"
    assert FeatureDefsDoc.format_display_name("cell-line") == "Cell Line"
    assert FeatureDefsDoc.format_display_name("the-mock-input") == "The Mock Input"


@patch("questionary.text")
def test_get_column_data(mock_questionary_text):
    mock_questionary_text.return_value.unsafe_ask.return_value = "mocked_input"
    mock_data_loader = MagicMock(spec=DataLoader)
    handler = DatasetInputHandler(path="dummy_path", output_path="dummy_output_path")
    inputs = handler.inputs
    mock_data_loader.data = [
        {
            "cell_id": "3",
            "parent_id": "7649",
            "cell_group": "AICS-22",
            "cell-surface-area (\\u00b5m\\u00b2)": "1429.4477",
            "interphase-or-mitosis (stage)": "0",
        }
    ]
    feature_defs_doc = FeatureDefsDoc(mock_data_loader.data, inputs)
    column_data = feature_defs_doc.get_column_data("cell_id")
    assert column_data == ["3"]
    column_data = feature_defs_doc.get_column_data("parent_id")
    assert column_data == ["7649"]


@patch("questionary.text")
def test_get_row_data(mock_questionary_text):
    mock_questionary_text.return_value.unsafe_ask.return_value = "mocked_input"
    handler = DatasetInputHandler(path="dummy_path", output_path="dummy_output_path")
    inputs = handler.inputs
    mock_data_loader = MagicMock(spec=DataLoader)
    mock_data_loader.data = {
        "cell_id": "3",
        "parent_id": "7649",
        "cell_group": "AICS-22",
        "cell-surface-area (\\u00b5m\\u00b2)": "1429.4477",
        "interphase-or-mitosis (stage)": "0",
    }

    writer = DatasetWriter(inputs, mock_data_loader)

    file_info, features = writer.get_row_data(mock_data_loader.data)

    assert file_info == [3, 7649, "AICS-22"]
    assert features == [1429.4477, 0]
