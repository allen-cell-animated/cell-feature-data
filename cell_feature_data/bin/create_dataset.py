from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from cell_feature_data.user_input_handler import (
    DatasetInputHandler,
    MegasetInputHandler,
)
from cell_feature_data.data_loader import DataLoader, DatasetWriter
from cell_feature_data import constants

import questionary


def main():
    output_path = questionary.text(
        "Enter the output folder path (default: 'data'):",
        default="data",
    ).ask()

    dataset_type = questionary.select(
        "Select the type of dataset to create:",
        choices=["single dataset", "megaset"],
    ).ask()
    if dataset_type == "single dataset":
        create_single_dataset(output_path)
    else:
        create_megaset(output_path)


def create_single_dataset(output_path: str):
    file_path = questionary.text(
        "Enter a valid file path:",
        validate=lambda text: True if len(text) > 0 else "File path cannot be empty.",
    ).ask()

    # Initialize the user input handler, data loader and dataset writer
    input_handler = DatasetInputHandler(file_path)
    init_inputs = input_handler.inputs
    loader = DataLoader(init_inputs, input_handler.path)
    writer = DatasetWriter(init_inputs, loader)

    writer.process_data()
    writer.create_dataset_folder(output_path)

    additional_settings = questionary.select(
        "How do you want to add additional settings for the dataset?",
        choices=["By prompts", "Manually edit the JSON files later"],
    ).ask()

    if additional_settings == "By prompts":
        input_handler.dataset_writer = writer
        additional_inputs = input_handler.get_additional_settings()
        dataset_filepath = writer.json_file_path_dict.get(constants.DATASET_FILENAME)
        writer.update_json_file_with_additional_data(
            dataset_filepath, asdict(additional_inputs)
        )


def create_megaset(output_path: str):
    input_handler = MegasetInputHandler()
    init_inputs = input_handler.inputs
    megaset_folder_path = (
        Path(output_path) / f"{init_inputs.name}_{datetime.utcnow().year}"
    )
    megaset_folder_path.mkdir(parents=True, exist_ok=True)

    # TODO: collect single dataset names to be included in dataset.json
    # TODO: when creating megasets, change the name of each single set folder. e.g."i1m1"
    # single_datasets = []

    next_dataset = "Yes"
    while next_dataset == "Yes":
        print(
            "Starting the process to create single datasets within the megaset---------"
        )
        create_single_dataset(output_path=megaset_folder_path)
        next_dataset = questionary.select(
            "Do you want to create another dataset?", choices=["Yes", "No"]
        ).ask()
    # create the high-level dataset.json
    writer = DatasetWriter(inputs=init_inputs)
    writer.write_json_files(megaset_folder_path, dataset_type="megaset")
    additional_settings = questionary.select(
        "How do you want to add settings for the megaset?",
        choices=["By prompts", "Manually edit the JSON file later"],
    ).ask()
    if additional_settings == "By prompts":
        additional_inputs = input_handler.get_settings_for_megaset()
        dataset_filepath = writer.json_file_path_dict.get(
            constants.MEGASET_DATASET_FILENAME
        )
        writer.update_json_file_with_additional_data(
            dataset_filepath, asdict(additional_inputs)
        )


if __name__ == "__main__":
    main()
