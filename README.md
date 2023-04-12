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
