# Automate-print

Automate-print is a project that aims to automate creation of all printables. Based on HTML templates PDF files are generated using [Weasyprint]

This repository also [contains information](/data/) regarding lectures schedules over years and places description.

## Overview of solution

- We generate HTML templates for Weasyprint using following data:
  * place - yaml file that contains descriptions of attractions that are available nearby, needs to be updated manually to fit the location. Those files are kept in this repository in `data/places`.
  * schedule - csv file that contains schedule of the conference generated in the scheduler-spreadsheet.
  * data - json file to be exported from the Zosia website.

- Templates and PDFs generation, as well as data validation is done by `print.py` script.
- Generated files will be placed in the `gen` directory.

## Usage

### Dependencies

In order to run the project you need following dependencies:
- python3
- (optional) python3-venv

### Windows

Because of weasyprint dependency, currently, Only Windows 11 64-bit is supported. Additionally, you will need [GTK3 for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) (please refer to [weasyprint page](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)) to run this project.

### Install requirements

You can install requirements for your system:
```console
python3 -m pip install -r requirements.txt
```

or create virtual environment and install dependencies inside:
```console
python3 -m venv zosia_print_venv
source zosia_print_venv/bin/activate
python3 -m pip install -r requirements.txt
```

_Note: If you want to deactivate your virtual environment use_ `deactivate` _command._

### Run

```console
python3 zosia_print.py <options>
```

**Examples:**
```console
python3 zosia_print.py --help
python3 zosia_print.py --place Mieszko --schedule Plan.csv
python3 zosia_print.py --place Marcus --schedule NewPlan.csv --data some-test-data.json
python3 zosia_print.py --place Mieszko --schedule Plan2.csv --blanks 50
python3 zosia_print.py --schedule Plan.csv --place Marcus --render identifiers --debug
```
