from dataclasses import asdict

from python_dataset_creator.user_input_handler import DatasetInputHandler
from python_dataset_creator.data_loader import DataLoader, DatasetWriter
from python_dataset_creator import constants

import questionary


def main():
    file_path = questionary.text(
        "Enter a valid file path:",
        validate=lambda text: True if len(text) > 0 else "File path cannot be empty.",
    ).ask()

    output_path = questionary.text(
        "Enter the output folder path (default: 'data'):",
        default="data",
    ).ask()

    # Initialize the user input handler, data loader and dataset writer
    input_handler = DatasetInputHandler(file_path)
    init_inputs = input_handler.inputs
    loader = DataLoader(init_inputs, input_handler.path)
    writer = DatasetWriter(loader, init_inputs)

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


if __name__ == "__main__":
    main()
