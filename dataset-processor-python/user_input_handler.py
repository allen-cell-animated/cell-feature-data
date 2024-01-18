from pathlib import Path
import questionary
import re


class UserInputHandler:
    """
    Class to handle user inputs
    """

    def __init__(self, path, dataset_writer=None):
        self.path = Path(path)
        self.dataset_name = self.path.stem
        self.dataset_writer = dataset_writer
        self.inputs = self.get_initial_settings()

    @staticmethod
    def is_valid_version(version):
        pattern = r"^[0-9]{4}\.[0-9]+$"
        return re.match(pattern, version) is not None

    @staticmethod
    def is_feature_in_list(input, features):
        return input in features

    def get_initial_settings(self):
        version = questionary.text(
            "Enter the version(yyyy.number):",
            default="2024.0",
            validate=self.is_valid_version,
        ).ask()
        return {
            "path": self.path,
            "dataset_name": self.dataset_name,
            "version": version.strip(),
        }

    def get_questionary_input(self, prompt, default=None, validator=None, choices=None):
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

    def get_feature(self, prompt, features, default_index=0):
        """
        Get feature input from the user
        """
        if not features or default_index >= len(features) or default_index < 0:
            print("Error: Invalid feature list or default index.")
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
            print("Error: Dataset writer not initialized.")
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
        xAxis = self.get_feature(
            "Enter the feature name for xAxis default:", cell_features
        )
        yAxis = self.get_feature(
            "Enter the feature name for yAxis default:", cell_features, default_index=1
        )
        color_by = self.get_feature(
            "Enter the feature name for colorBy:", cell_features
        )
        group_by = self.get_feature(
            "Enter the feature name for groupBy:", discrete_features
        )

        return {
            "title": title,
            "description": description,
            "thumbnailRoot": thumbnail_root,
            "downloadRoot": download_root,
            "volumeViewerDataRoot": volume_viewer_data_root,
            "xAxis": {"default": xAxis, "exclude": []},
            "yAxis": {"default": yAxis, "exclude": []},
            "colorBy": {"default": color_by},
            "groupBy": {"default": group_by},
        }
