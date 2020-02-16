
{% for d in days %}
# {{ d.name }}
{% for e in d.events %}
- {{ e.startTime }} | {{ e.title }} | {{ e.lecturer }} {% endfor %}
{% endfor %}


