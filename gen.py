import difflib
import json
import yaml

from jinja2 import Environment, FileSystemLoader


NUMBER_OF_BLANK_IDENTIFIERS = 20
ZOSIA_DATE = "02.03.2023 - 05.03.2023"
HIGHLIGHTED_ORGANIZATIONS = {
    "FINGO": "gold",
    "Ten Square Games": "gold",
    "Antmicro": "gold"
}

env = Environment(loader=FileSystemLoader('./'))


def load_yaml_file(path):
    with open(path, "r", encoding="utf-8") as file:
        file_content = file.read()
        file_data = yaml.load(file_content, Loader=yaml.Loader)
        return file_data


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        file_content = file.read()
        file_data = json.loads(file_content)
        return file_data


def write_to_file(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def render(template, context):
    template = env.get_template(template)
    return template.render(context)


def make_indetifier_context(data):
    prefs = []
    for p in data["preferences"]:
        prefs.append({
            "first_name": p["user__first_name"],
            "last_name": p["user__last_name"],
            "organization": p["organization__name"],
            "highlight": HIGHLIGHTED_ORGANIZATIONS[p["organization__name"]] if p["organization__name"] in HIGHLIGHTED_ORGANIZATIONS else "none",
            "dinner_1": p["dinner_day_1"],
            "breakfast_2": p["breakfast_day_2"],
            "dinner_2": p["dinner_day_2"],
            "breakfast_3": p["breakfast_day_3"],
            "dinner_3": p["dinner_day_3"],
            "breakfast_4": p["breakfast_day_4"],
        })

    blank_identifiers = NUMBER_OF_BLANK_IDENTIFIERS
    for _ in range(blank_identifiers):
        prefs.append({
            "first_name": "..............",
            "last_name": "..............",
            "organization": ".............",
            "dinner_1": True,
            "breakfast_2": True,
            "dinner_3": True,
            "breakfast_3": True,
            "dinner_4": True,
            "breakfast_4": True,
        })

    return {"prefs": prefs, "camp_date": ZOSIA_DATE}


def gen_identifier(data):
    context = make_indetifier_context(data)
    rendered = render("identifier/identifier_template.html", context)
    write_to_file("gen/identifier.html", rendered)


def get_lecture_with_close_title(title, data):
    titles = [lecture["title"] for lecture in data["lectures"]]
    best_title = difflib.get_close_matches(title, titles)
    best_title_index = titles.index(best_title[0])
    return data["lectures"][best_title_index]


def calculate_end_time(start_time, duration):
    if duration == 0:
        return ""
    x = start_time.split(':')
    m = (int(x[1]) + duration)
    h = int(x[0]) + m // 60
    m = m % 60
    h = h % 24
    m = str(m) if len(str(m)) == 2 else "0" + str(m)
    h = str(h) if len(str(h)) == 2 else "0" + str(h)
    return str(h) + ":" + str(m)


def combine_schedule_event_and_data(schedule_event, data):
    end_time = calculate_end_time(schedule_event["startTime"], schedule_event["duration"])
    if schedule_event["type"] != "LECTURE":
        return {
            **schedule_event,
            "endTime": end_time,
        }
    lecture_data = get_lecture_with_close_title(schedule_event["title"], data)
    return {
        **schedule_event,
        "endTime": end_time,
        "abstract": lecture_data["abstract"].split('\n'),
        "title": lecture_data["title"],
        "lecturer": lecture_data["author__first_name"] + " " + lecture_data["author__last_name"],
        "organization": lecture_data["author__preferences__organization__name"],
    }


def combine_schedule_and_data(schedule, data):
    result = []
    for day in schedule:
        day_sched = [combine_schedule_event_and_data(e, data) for e in day["events"]]
        result.append({
            "name": day["name"],
            "session_name": day["session_name"],
            "events": day_sched,
        })
    return result


def gen_book_and_schedule(schedule, data):
    days = combine_schedule_and_data(schedule, data)

    book_template = env.get_template('book/book_template.html')
    string = book_template.render({"days": days, "places": places})
    with open("gen/book.html", "w", encoding="utf-8") as text_file:
        text_file.write(string)

    schedule_template_html = env.get_template('schedule/schedule_template.html')
    string = schedule_template_html.render({"days": days})
    with open("gen/schedule.html", "w", encoding="utf-8") as text_file:
        text_file.write(string)

    schedule_template_html = env.get_template('schedule/web_schedule_template.html')
    string = schedule_template_html.render({"days": days})
    with open("gen/web_schedule.html", "w", encoding="utf-8") as text_file:
        text_file.write(string)


if __name__ == "__main__":
    schedule = load_yaml_file("schedule.yaml")
    places = load_yaml_file("places.yaml")
    data = load_json_file("data.json")

    gen_identifier(data)
    gen_book_and_schedule(schedule, data)
