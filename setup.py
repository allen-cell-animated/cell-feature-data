from setuptools import setup, find_packages

requirements = [
"black>=23.12.1",
"click>=8.1.7",
"mypy-extensions>=1.0.0",
"numpy>=1.26.3",
"packaging>=23.2",
"pandas>=2.1.4",
"pathspec>=0.12.1",
"platformdirs>=4.1.0",
"prompt-toolkit>=3.0.36",
"python-dateutil>=2.8.2",
"pytz>=2023.3.post1",
"questionary>=2.0.1",
"six>=1.16.0",
"tzdata>=2023.4",
"wcwidth>=0.2.13",
]

setup(
    name='creator',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'create-dataset = python_dataset_creator.bin.create_dataset:main',
        ],
    },
    install_requires= requirements,
    version='1.0.0',
    python_requires='>=3.8',
)