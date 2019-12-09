from jinja2 import Environment, FileSystemLoader
import difflib

NUMBER_OF_IDENTIFIERS = 11

def load_yaml_file(path):
    import yaml
    with open(path, "r") as f:
        file_content = f.read()
        file_data = yaml.load(file_content)
        return file_data

def load_json_file(path):
    import json
    with open(path, "r") as f:
        file_content = f.read()
        file_data = json.loads(file_content)
        return file_data

schedule = load_yaml_file("schedule.yaml");
data = load_json_file("data.json");

def write_to_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def render(template, context):
    template = env.get_template(template)
    return template.render(context)

def make_indetifier_context(data):
    prefs = []
    print (data)
    for p in data["preferences"][:11]:
        print(p)
        prefs.append({
            "first_name": p["user__first_name"],
            "last_name": p["user__last_name"],
            "organization": p["organization_id__name"],
            "dinner_1": p["dinner_1"],
            "breakfast_2": p["breakfast_2"],
            "dinner_2": p["dinner_2"],
            "breakfast_3": p["breakfast_3"],
            "dinner_3": p["dinner_3"],
            "breakfast_4": p["breakfast_4"],
        })

    blank_identifiers = NUMBER_OF_IDENTIFIERS - len(prefs)
    for _ in range(blank_identifiers):
        prefs.append({
            "first_name": "..............",
            "last_name": "..............",
            "organization": ".............",
            "dinner_1": True,
            "breakfast_2": True,
            "dinner_2": True,
            "breakfast_3": True,
            "dinner_3": True,
            "breakfast_4": True,
        })
    
    return {"prefs": prefs}

def gen_identifier(data):
    context = make_indetifier_context(data)
    rendered = render("identifier/identifier_template.html", context)
    write_to_file("gen/identifier.html", rendered)

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

def gen_book_and_schedule(schedule, data):
    days = combine_schedule_and_data(schedule, data)

    book_template = env.get_template('book/book_template.html')
    string=book_template.render({"days": days})
    with open("gen/book.html", "w") as text_file:
        text_file.write(string)

    schedule_template_html = env.get_template('schedule/schedule_template.html')
    string=schedule_template_html.render({"days": days})
    with open("gen/schedule.html", "w") as text_file:
        text_file.write(string);

    schedule_template_md = env.get_template('schedule/schedule_template.md')
    string=schedule_template_md.render({"days": days})
    with open("gen/schedule.md", "w") as text_file:
        text_file.write(string)

    
env = Environment(loader=FileSystemLoader('./'))
gen_identifier(data)
gen_book_and_schedule(schedule, data)
