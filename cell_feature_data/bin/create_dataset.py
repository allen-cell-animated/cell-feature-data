from pathlib import Path
from datetime import datetime
from dataclasses import asdict
import sys

from cell_feature_data.user_input_handler import (
    DatasetInputHandler,
    MegasetInputHandler,
)
from cell_feature_data.data_loader import DataLoader, DatasetWriter
from cell_feature_data import constants

import questionary


def main():
    try:
        output_path = questionary.path(
            "Enter the output folder path (default: 'data'):",
            default="data",
            validate=lambda text: (
                True if len(text) > 0 else "Output path cannot be empty."
            ),
        ).unsafe_ask()

        dataset_type = questionary.select(
            "Select the type of dataset to create:",
            choices=["single dataset", "megaset"],
        ).unsafe_ask()
        if dataset_type == "single dataset":
            create_single_dataset(output_path)
        elif dataset_type == "megaset":
            create_megaset(output_path)
    except KeyboardInterrupt:
        exit_message(folder_created=False)


def exit_message(folder_created: bool = True):
    if folder_created:
        print(
            "Keyboard interrupt detected, exiting the process. Please edit the JSON file to continue."
        )
    else:
        print(
            "Keyboard interrupt detected, exiting the process. Please run the script again to continue."
        )
    sys.exit(0)


def create_single_dataset(output_path: str, for_megaset: bool = False):
    file_path = questionary.path(
        "Enter a valid file path:",
        validate=lambda text: True if len(text) > 0 else "File path cannot be empty.",
    ).unsafe_ask()

    # Initialize the user input handler, data loader and dataset writer
    input_handler = DatasetInputHandler(file_path, output_path=output_path)
    init_inputs = input_handler.inputs
    loader = DataLoader(init_inputs, input_handler.path)
    writer = DatasetWriter(init_inputs, loader, for_megaset)

    writer.process_data()
    writer.create_dataset_folder(output_path)
    try:
        additional_settings = questionary.select(
            "How do you want to add additional settings for the dataset?",
            choices=["By prompts", "Manually edit the JSON files later"],
        ).unsafe_ask()
        if additional_settings == "By prompts":
            input_handler.dataset_writer = writer
            additional_inputs = input_handler.get_additional_settings()
            dataset_filepath = writer.json_file_path_dict.get(
                constants.DATASET_FILENAME
            )
            writer.update_json_file_with_additional_data(
                dataset_filepath, asdict(additional_inputs)
            )
        return init_inputs.name, writer.updated_dataset_list

    except KeyboardInterrupt:
        exit_message()


def create_megaset(output_path: str):
    input_handler = MegasetInputHandler()
    init_inputs = input_handler.inputs
    megaset_folder_path = (
        Path(output_path) / f"{init_inputs.name}_{datetime.utcnow().year}"
    )
    megaset_folder_path.mkdir(parents=True, exist_ok=True)
    next_dataset = True

    while next_dataset:
        print(
            "Starting the process to create single datasets within the megaset---------"
        )
        dataset_name, dataset_list = create_single_dataset(
            output_path=megaset_folder_path, for_megaset=True
        )
        init_inputs.datasets.append(dataset_name)

        next_dataset = questionary.confirm(
            "Do you want to add another dataset to the megaset?"
        ).unsafe_ask()

    try:
        # create the top-level dataset.json
        print("Creating the top-level dataset.json file for the megaset---------")
        writer = DatasetWriter(inputs=init_inputs, for_megaset=True)
        writer.write_json_files(megaset_folder_path, write_megaset=True)
        additional_settings = questionary.select(
            "How do you want to add settings for the megaset?",
            choices=["By prompts", "Manually edit the JSON file later"],
        ).unsafe_ask()
        if additional_settings == "By prompts":
            additional_inputs = input_handler.get_settings_for_megaset()
            dataset_filepath = writer.json_file_path_dict.get(
                constants.MEGASET_DATASET_FILENAME
            )
            # update the datasets in dataset.json file if a new dataset is added
            if dataset_list:
                additional_inputs.datasets = dataset_list
            writer.update_json_file_with_additional_data(
                dataset_filepath, asdict(additional_inputs)
            )
    except KeyboardInterrupt:
        exit_message()


if __name__ == "__main__":
    main()
