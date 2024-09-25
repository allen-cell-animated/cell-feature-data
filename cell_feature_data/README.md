# Cell Feature Data

[![Dataset validation](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/validate.yml)


**Python Package for Creating and Validating Cell Feature Datasets for [Cell Feature Explore](https://cfe.allencell.org/)**

---

## Documentation

For full documentation, please see the [full documentation on Github](https://github.com/allen-cell-animated/cell-feature-data).

---

## Install and Setup

```pip install cell-feature-data```

## To create a new dataset using the package:
1. Create a virtual environment if not already created: `python3 -m venv [ENV-PATH]`
2. Activate the virtual environment: 
   - On macOS/Linux: `source [ENV-PATH]/bin/activate`
   - On Windows: `[ENV-PATH]\Scripts\activate`
3. Install the dependencies: `pip install cell-feature-data`. 
4. Run `create-dataset` to start the dataset creation process. This will: 
   - Request the path of the file you want to process. Formats supported: `.csv`, with more formats to be added as development progresses
   - Ask for an output path to save your dataset. If not specified, a new dataset folder is created in `data`, named after the input file
   - Process the input file and generate the necessary json files for the dataset
   - Prompt for additional information about the dataset and update the json files accordingly
5. Deactivate the virtual environment when finished: `deactivate`

#### For more on what these files should look like, look at [Full spec documentation](https://allen-cell-animated.github.io/cell-feature-data/HandoffSpecification.html)

**MIT license**