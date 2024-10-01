# Cell Feature Data

[![Dataset validation](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/allen-cell-animated/cell-feature-data/actions/workflows/validate.yml)


**Python Package for Creating and Validating Cell Feature Datasets for [Cell Feature Explore](https://cfe.allencell.org/)**

---

## Documentation

For full documentation, please see the [full documentation on Github](https://github.com/allen-cell-animated/cell-feature-data).


## Installation

```pip install cell-feature-data```

## Usage
### Create a single dataset or a megaset for the Cell Feature Explore:

Run the following command in your terminal:
```create-dataset```

### This command will guide you through the following steps: 
  1. **Specify the Path to the Input File:** 
      Supported formats: `.csv` (with more formats to be added in future releases).
  2. **Set the Output Directory:**
      Provide a path to save the generated dataset files. If not specified, a new dataset folder will be created in the `data` directory, named after the input file.
  3. **Process the input file:**
      The tool will calculate and generate the necessary JSON files based on the input data.
  4. **Enter Additional Metadata:** 
      You will be prompted to add more details about the dataset, which will be used to update the generated JSON files.

### Import and use the package within your python scripts:
```
   from cell_feature_data.bin.create_dataset import main


   # Call the main function
   if __name__ == "__main__":
      main()
```

## Dataset Specification 
For more information on the dataset structure and settings, refer to the [Full spec documentation](https://allen-cell-animated.github.io/cell-feature-data/HandoffSpecification.html)