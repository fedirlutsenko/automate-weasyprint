import os
import csv
import sys
import json
import locale
import argparse

from datetime import date, timedelta
from typing import List, Dict, Any, Optional

import yaml

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


PLACES_PATH = "./data/places"
SCHEDULES_PATH = "./data/schedules"
TEMPLATES_PATH = "./templates"
TARGET_DIR = "./gen"
DEBUG_MODE = False
env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))


def load_yaml_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        file_data = yaml.load(file.read(), Loader=yaml.Loader)
        return file_data


def load_json_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        file_data = json.loads(file.read())
        return file_data


def generate_schedule(path: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    weekdays = [d.strftime("%A") for d in [
        date.today() + timedelta(days=i) for i in range(7)]]

    schedule: List[Dict[str, Any]] = []
    lectures = {lect['title']: lect for lect in data['lectures']}

    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        day_name = None
        session_name = None
        events: List[Dict[str, Any]] = []

        for row in reader:
            if row[0].lower() in weekdays:
                if len(events) > 0:
                    schedule.append({
                        "name": day_name,
                        "session_name": session_name,
                        "events": events,
                    })

                day_name = row[0].title()
                session_name = row[1] if row[1] != '' else day_name
                events = []

                # skip header row:
                next(reader)
                continue

            if row[0] == '':
                # skip empty rows
                continue

            (start_time, lecturer, printing_title, title, end_time,
             break_time, event_type, comments, sponsor, service,
             additional_comments, duration) = row

            # NOTE: these structures are backward compatible with old templates
            if event_type.lower() != "lecture":
                events.append({
                    "title": printing_title,
                    "type": event_type.lower(),
                    "startTime": start_time,
                    "duration": duration,
                    "endTime": end_time,
                })
                continue

            # TODO: Handle some typos or other small mismatches
            if title not in lectures:
                print_warning(f"Lecture '{title}' not found in data file. "
                              f"Skipping...")
                continue

            lecture_data = lectures[title]

            # Support for files modified on Windows...
            paragraph_mark = '\n\n'
            if '\r\n' in lecture_data['abstract']:
                paragraph_mark = '\r\n\r\n'

            events.append({
                "type": event_type.lower(),
                "startTime": start_time,
                "duration": duration,
                "endTime": end_time,
                "abstract": lecture_data['abstract'].split(paragraph_mark),
                "title": printing_title,
                "lecturer": lecturer,
                "organization": sponsor,
            })

    schedule.append({
        "name": day_name,
        "session_name": session_name,
        "events": events,
    })

    return schedule


def get_options(path: str) -> List[str]:
    return [f.rstrip(".yaml") for f in os.listdir(path)]


def render_template(template: str, context: Dict[str, Any]) -> Any:
    return env.get_template(template).render(context)


def print_warning(*args: Any) -> None:
    print("\u001b[35;1m[Warning]\u001b[0m", *args, file=sys.stderr)


def render_document(
        path: str, ctx: Dict[str, Any], name: Optional[str] = None,
        html_output: bool = False) -> None:
    template_dir = path.rsplit('/', 1)[0]
    target_name = name if name is not None else template_dir
    target_file = f"{TARGET_DIR}/{target_name}"

    if not html_output:
        # PDF output
        HTML(
            string=render_template(path, ctx),
            base_url=f"{TEMPLATES_PATH}/{template_dir}"
        ).write_pdf(
            f"{target_file}.pdf",
            font_config=FontConfiguration())

    if html_output or DEBUG_MODE:
        with open(f"{target_file}.html", "w", encoding="utf-8") as file:
            file.write(render_template(path, ctx))


def extract_preferences(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    pref = []
    for p in data["preferences"]:
        organization = p["organization__name"]
        if organization is not None and len(organization) > 80:
            print_warning(f"Organization name: \"{organization}\" is to long"
                          f"and will be truncated.")
            organization = organization[:80] + '...'

        pref.append({
            "first_name": p["user__first_name"],
            "last_name": p["user__last_name"],
            "organization": organization,
            # TODO: Add highlights
            # "highlight": HIGHLIGHTED_ORGANIZATIONS[p["organization__name"]] if p["organization__name"] in HIGHLIGHTED_ORGANIZATIONS else "none",
            "dinner_1": p["dinner_day_1"],
            "breakfast_2": p["breakfast_day_2"],
            "dinner_2": p["dinner_day_2"],
            "breakfast_3": p["breakfast_day_3"],
            "dinner_3": p["dinner_day_3"],
            "breakfast_4": p["breakfast_day_4"],
        })

    return pref


def main() -> None:
    places_list = get_options(PLACES_PATH)
    today = date.today()
    edition = today.year if today.month <= 3 else today.year + 1

    parser = argparse.ArgumentParser(
        description="Zosia-print - generates printables based on the HTML "
                    "templates and data from Zosia website.")
    parser.add_argument('--place', choices=places_list, required=True,
                        help="Name of the place where Zosia will be held.")
    parser.add_argument('--schedule', help="Path to CSV file with schedule "
                        "from schedule spreadsheet for this year.")
    parser.add_argument('--data', default='data.json', help="Path to JSON file"
                        "generated by Zosia website.")
    parser.add_argument('--blanks', type=int, default=20, dest='n_of_blanks',
                        help="Number of blank identifiers.")
    parser.add_argument('--debug', action='store_true', help="Render separate "
                        "HTML file for each PDF export.")

    args = parser.parse_args()
    print(args)

    # Use global variable to simplify configuring debugs
    global DEBUG_MODE
    DEBUG_MODE = args.debug

    # Make sure that target directory exist
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Enforce polish locale to generate proper month name
    locale.setlocale(locale.LC_ALL, 'pl_PL.utf8')

    # Load data
    data = load_json_file(args.data)
    place = load_yaml_file(f"{PLACES_PATH}/{args.place}.yaml")
    schedule = generate_schedule(args.schedule, data)

    # Render Zosia date
    start_date = date.fromisoformat(data["zosia"]["start_date"])
    end_date = date.fromisoformat(data["zosia"]["end_date"])
    zosia_date = f"{start_date:%-d} - {end_date:%-d %B %Y}"
    if start_date.month != end_date.month:
        zosia_date = f"{start_date:%-d %B} - {end_date:%-d %B %Y}"

    print(f"Zosia {edition} - camp date: {zosia_date}")

    # TODO: Validate data
    # TODO: Load information about highlighted organizations
    # and contacts to organizers

    contacts = {
      "Aneta Kos": "111 222 333",
      "Jan Kowalski": "222 333 444",
      "Bartosz Kurek": "123 456 789",
    }

    # Book
    print("Rendering book...")
    render_document("book/book_template.html", {
        "days": schedule,
        "place": place,
        "contacts": contacts,
        "camp_date": zosia_date
    })

    # Schedule
    print("Rendering schedule...")
    render_document("schedule/schedule_template.html", {
        "days": schedule
    })

    # Web schedule for zosia-site
    render_document("schedule/web_schedule_template.html", {
                        "days": schedule
                    }, "web_schedule", True)

    # Identifier
    print("Rendering identifiers...")
    blanks = [{'template': True}] * args.n_of_blanks
    render_document("identifier/identifier_template.html", {
        "prefs": extract_preferences(data) + blanks,
        "camp_date": zosia_date,
        "location": place['localization'],
    })


if __name__ == "__main__":
    main()
