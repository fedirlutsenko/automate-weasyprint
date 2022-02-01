# zosia_print

Zosia print is a project that aims to automate creation of all printables that are needed at ZOSIA conference.

## Overview of solution

- We generate printables using following data:
  * places.yaml - contains descriptions of attractions that are availble nearby, needs to be updated manually to fit the location/
  * schedule.yaml - contains schedule of the conference. Here is a quick overview of the format:
    ~~~
    - name: <Name on the plan>
      session_name: <Name near the lecture description>
      events:
              - title: <event title> (must match title on the website if it's a lecture)
                type: <event type> (possible values: LECTURE, MEAL)
                startTime: <start time> (using format "hh:mm")
                duration: <length of event in minutes>
    ~~~
  * data.json - json file to be exported from zosia website
- We use gen.py script to generate the .html files from jinja templates and files mentioned above.
- Generated .html files are transformed into pdfs using a tool called weasyprint.

## Usage

### Dependencies

In order to run the project you need following dependencies:
- python-3.8
- pipenv

### Install

~~~
pipenv install
~~~

### Run

~~~
make all
~~~
