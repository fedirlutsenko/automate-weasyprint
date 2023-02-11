import os
import csv
import sys
import json
import argparse

from datetime import date, timedelta
from typing import List, Dict, Any, Optional

import yaml

from babel.dates import format_interval, format_date
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


PLACES_PATH = "./data/places"
SCHEDULES_PATH = "./data/schedules"
TEMPLATES_PATH = "./templates"
TARGET_DIR = "./gen"
DEBUG_MODE = False
LOCALE = 'pl'

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
    weekdays = [format_date(d, format='EEEE', locale=LOCALE) for d in [
        date.today() + timedelta(days=i) for i in range(7)]]

    schedule: List[Dict[str, Any]] = []
    lectures = {lect['title']: lect for lect in data['lectures']}
    sponsors = {spon['name']: spon for spon in data['sponsors']}

    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        day_name = None
        session_name = None
        events: List[Dict[str, Any]] = []

        def has_lecture(events: List[Dict[str, Any]]) -> bool:
            return any(e['type'].lower() == "lecture" for e in events)

        for row in reader:
            if row[0].lower() in weekdays:
                if len(events) > 0:
                    schedule.append({
                        "name": day_name,
                        "session_name": session_name,
                        "events": events,
                        "has_lecture": has_lecture(events),
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
             break_time, event_type, comments, highlighted, service,
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

            organization = lecture_data[
                'author__preferences__organization__name']

            highlight_type = 'none'

            # Highlight Lecture
            if highlighted.lower() == "yes":
                if organization not in sponsors:
                    print_warning(
                        f"Lecture '{title}' should be highlighted, but "
                        f"organization '{organization}' was not found in "
                        f"the data file. Skipping highlighting...")
                else:
                    highlight_type = sponsors[organization]['sponsor_type']

            events.append({
                "type": event_type.lower(),
                "startTime": start_time,
                "duration": duration,
                "endTime": end_time,
                "abstract": lecture_data['abstract'].split(paragraph_mark),
                "title": printing_title,
                "lecturer": lecturer,
                "showOrganization": highlighted.lower() == "yes" and organization in sponsors,
                "highlight": highlight_type,
                "organization": organization,
            })

    # Add the rest of the events to the schedule
    schedule.append({
        "name": day_name,
        "session_name": session_name,
        "events": events,
        "has_lecture": has_lecture(events),
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
    sponsors = {spon['name']: spon for spon in data['sponsors']}

    for p in data["preferences"]:
        organization = p['organization__name']
        if organization is not None and len(organization) > 80:
            print_warning(f"Organization name: \"{organization}\" is too long"
                          f"and will be truncated.")
            organization = organization[:80] + '… '

        person_type = p['user__person_type'].lower()
        first_name = p['user__first_name']
        last_name = p['user__last_name']

        # Highlight Organization
        highlight_type = "none"

        if person_type == "organizer":
            highlight_type = "organizer"

        elif person_type == "sponsor": 
            if organization in sponsors:
                highlight_type = sponsors[organization]['sponsor_type']

            else: 
                print_warning(f"'{first_name} {last_name}' is listed as a sponsor "
                              f"but organization '{organization}' was not found "
                              f"in the data file. Skipping highlighting...")

        elif person_type != "sponsor" and organization in sponsors:
            print_warning(f"'{first_name} {last_name}' "
                          f"is from the '{organization}' but is not listed as "
                          f"a sponsor. Skipping highlighting...")

        if DEBUG_MODE:
            print(
                f"{first_name + ' ' + last_name:<30} - "
                f"{str(organization):<50} - {highlight_type}")

        pref.append({
            "first_name": first_name,
            "last_name": last_name,
            "organization": organization,
            "highlight": highlight_type,
            "dinner_1": p['dinner_day_1'],
            "breakfast_2": p['breakfast_day_2'],
            "dinner_2": p['dinner_day_2'],
            "breakfast_3": p['breakfast_day_3'],
            "dinner_3": p['dinner_day_3'],
            "breakfast_4": p['breakfast_day_4'],
        })

    return pref


def main() -> None:
    places_list = get_options(PLACES_PATH)
    today = date.today()
    edition = today.year if today.month <= 3 else today.year + 1

    render_options = (['all'] + os.listdir(TEMPLATES_PATH) +
                      [f"{obj}s" for obj in os.listdir(TEMPLATES_PATH)])

    parser = argparse.ArgumentParser(
        description="Zosia-print - generates printables based on the HTML "
                    "templates and data from Zosia website.")
    parser.add_argument('--place', choices=places_list, required=True,
                        help="Name of the place where Zosia will be held.")
    parser.add_argument('--schedule', required=True, help="Path to CSV file "
                        "with schedule from schedule spreadsheet.")
    parser.add_argument('--data', default='data.json', help="Path to JSON file"
                        "generated by Zosia website.")
    parser.add_argument('--blanks', type=int, default=20, dest='n_of_blanks',
                        help="Number of blank identifiers.")
    parser.add_argument('--debug', action='store_true', help="Render separate "
                        "HTML file for each PDF export.")
    parser.add_argument('--render', default='all', choices=render_options,
                        help="Choose object to render (all by default).")

    args = parser.parse_args()
    print(args)

    # Use global variable to simplify configuring debugs
    global DEBUG_MODE  # pylint: disable=W0603
    DEBUG_MODE = args.debug

    # Make sure that target directory exist
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Load data
    data = load_json_file(args.data)
    place = load_yaml_file(f"{PLACES_PATH}/{args.place}.yaml")
    schedule = generate_schedule(args.schedule, data)

    # Render Zosia date
    start_date = date.fromisoformat(data["zosia"]["start_date"])
    end_date = date.fromisoformat(data["zosia"]["end_date"])

    zosia_date = format_interval(start_date, end_date, 'yMMMMd', locale=LOCALE)

    print(f"Zosia {edition} - camp date: {zosia_date}")

    # TODO: Validate data

    render_all = args.render == 'all'
    if render_all or args.render.startswith('book'):
        # Book
        print("Rendering book...")
        render_document("book/book_template.html", {
            "days": schedule,
            "place": place,
            "contacts": data['contacts'],
            "camp_date": zosia_date,
            "sponsors": data['sponsors']
        })

    if render_all or args.render.startswith('schedule'):
        # Schedule
        print("Rendering schedule...")
        render_document("schedule/schedule_template.html", {
            "days": schedule
        })

        # Web schedule for zosia-site
        render_document("schedule/web_schedule_template.html", {
                            "days": schedule
                        }, "web_schedule", True)

    if render_all or args.render.startswith('identifier'):
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
