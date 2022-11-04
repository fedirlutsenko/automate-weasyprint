# Zosia-print

Zosia-print is a project that aims to automate creation of all printables that are needed at the ZOSIA conference. Based on HTML templates PDF files are generated using [Weasyprint](https://github.com/Kozea/WeasyPrint).

This repository also [contains information](/data/) regarding lectures schedules over years and places description.

## Overview of solution

- We generate HTML templates for Weasyprint using following data:
  * places - yaml file that contains descriptions of attractions that are available nearby, needs to be updated manually to fit the location/
  * schedule - yaml file that contains schedule of the conference. Here is a quick overview of the format:
    ~~~
    - name: <Name on the plan>
      session_name: <Name near the lecture description>
      events:
              - title: <event title> (must match title on the website if it's a lecture)
                type: <event type> (possible values: LECTURE, MEAL, EVENT, WORKSHOP)
                startTime: <start time> (using format "hh:mm")
                duration: <length of event in minutes>
    ~~~
  * data.json - json file to be exported from Zosia website

- Templates and PDFs generation, as well as data validation is done by `zosia_print.py` script.
- Generated files will be placed in the `gen` directory.

## Usage

### Dependencies

In order to run the project you need following dependencies:
- python3
- (optional) python3-venv

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
```