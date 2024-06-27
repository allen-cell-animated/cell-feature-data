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
    output_path = questionary.path(
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


def create_single_dataset(output_path: str, for_megaset: bool = False):
    file_path = questionary.path(
        "Enter a valid file path:",
        validate=lambda text: True if len(text) > 0 else "File path cannot be empty.",
    ).ask()

    # Initialize the user input handler, data loader and dataset writer
    input_handler = DatasetInputHandler(file_path, output_path=output_path)
    init_inputs = input_handler.inputs
    loader = DataLoader(init_inputs, input_handler.path)
    writer = DatasetWriter(init_inputs, loader, for_megaset)

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
    return init_inputs.name


def create_megaset(output_path: str):
    input_handler = MegasetInputHandler()
    init_inputs = input_handler.inputs
    megaset_folder_path = (
        Path(output_path) / f"{init_inputs.name}_{datetime.utcnow().year}"
    )
    megaset_folder_path.mkdir(parents=True, exist_ok=True)
    dataset_names = []
    next_dataset = True

    while next_dataset:
        print(
            "Starting the process to create single datasets within the megaset---------"
        )
        dataset_name = create_single_dataset(
            output_path=megaset_folder_path, for_megaset=True
        )
        dataset_names.append(dataset_name)
        init_inputs.datasets = dataset_names
        next_dataset = questionary.confirm(
            "Do you want to add another dataset to the megaset?"
        ).ask()

    # create the top-level dataset.json
    print("Creating the top-level dataset.json file for the megaset---------")
    writer = DatasetWriter(inputs=init_inputs, for_megaset=True)
    writer.write_json_files(megaset_folder_path, write_megaset=True)
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
