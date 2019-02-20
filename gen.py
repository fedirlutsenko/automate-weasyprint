from jinja2 import Environment, FileSystemLoader
import difflib
import json
import yaml

NUMBER_OF_IDENTIFIERS = 200

with open("schedule.yaml", "r") as yaml_file:
    yaml_content = yaml_file.read()
    schedule = yaml.load(yaml_content)

def gen_identifier(data):
    prefs = data["preferences"]
    name_and_meals = []
    for p in prefs:
        if not p["payment_accepted"]:
            continue
        name_and_meals.append({
            "first_name": p["user__first_name"],
            "last_name": p["user__last_name"],
            "dinner_1": p["dinner_1"],
            "breakfast_2": p["breakfast_2"],
            "dinner_2": p["dinner_2"],
            "breakfast_3": p["breakfast_3"],
            "dinner_3": p["dinner_3"],
            "breakfast_4": p["breakfast_4"],
        })

    blank_identifiers = NUMBER_OF_IDENTIFIERS - len(name_and_meals)
    for _ in range(blank_identifiers):
        name_and_meals.append({
            "first_name": "..............",
            "last_name": "..............",
            "dinner_1": True,
            "breakfast_2": True,
            "dinner_2": True,
            "breakfast_3": True,
            "dinner_3": True,
            "breakfast_4": True,
        })

    template = env.get_template('identifier/identifier_template.html')
    string=template.render({"prefs": name_and_meals})
    with open("gen/identifier.html", "w") as text_file:
        text_file.write(string)

def get_lecture_with_close_title(title, data):
    titles = [l["title"] for l in data["lectures"]]
    best_title = difflib.get_close_matches(title, titles);
    best_title_index = titles.index(best_title[0])
    return data["lectures"][best_title_index]

def combine_schedule_event_and_data(schedule_event, data):
    if schedule_event["type"] != "LECTURE":
        return schedule_event
    lecture_data = get_lecture_with_close_title(schedule_event["title"], data)
    return {
        **schedule_event,
        "abstract": lecture_data["abstract"].split('\n'),
        "title": lecture_data["title"],
        "lecturer": lecture_data["author__first_name"] + " " + lecture_data["author__last_name"],
    }

def combine_schedule_and_data(schedule, data):
    result = []
    for day in schedule:
        day_sched = [combine_schedule_event_and_data(e, data) for e in day["events"]]
        result.append({
            "name": day["name"],
            "events": day_sched,
        })
    return result

def gen_book(schedule, data):
    days = combine_schedule_and_data(schedule, data)
    template = env.get_template('book/book_template.html')
    string=template.render({"days": days})
    with open("gen/book.html", "w") as text_file:
        text_file.write(string)
    
env = Environment(loader=FileSystemLoader('./'))
with open("data.json", "r") as json_file:
    data = json_file.read()
    data = json.loads(data);
    gen_identifier(data);
    gen_book(schedule, data);
