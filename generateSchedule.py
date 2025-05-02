from datetime import datetime
from itertools import product

# filter out comboos with time conflicts, and violations of time preferences
# return clean JSON with each valid schedule

# mock data for now (eventually we'll query this from mySQL)

MOCK_SECTIONS = {
    "CS288": [
        {"section": "001", "day": "Monday", "start": "12:00 PM", "end": "1:20 PM", "mode": "In Person"},
        {"section": "002", "day": "Thursday", "start": "3:00 PM", "end": "4:20 PM", "mode": "Online"}
    ],
    "CS350": [
        {"section": "001", "day": "Monday", "start": "2:00 PM", "end": "3:20 PM", "mode": "Hybrid"},
        {"section": "002", "day": "Thursday", "start": "11:00 AM", "end": "12:20 PM", "mode": "In Person"}
    ],
    "CS435": [
        {"section": "001", "day": "Monday", "start": "4:00 PM", "end": "5:20 PM", "mode": "In Person"},
        {"section": "002", "day": "Thursday", "start": "1:00 PM", "end": "2:20 PM", "mode": "Online"}
    ]
}

def time_str_to_minutes(t):
    # convert time string into minutes since midnight
    # ex. "2:30 PM" becomes 14 * 60 + 30 = 870
    # ex. "11:00 AM" becomes 11 * 60 + 0 = 660
    dt = datetime.strptime(t, "%I:%M %p")
    return dt.hour * 60 + dt.minute

def is_within_preference(section, prefs):
    day = section["day"]
    if day not in prefs:
        return False
    start = time_str_to_minutes(section["start"])
    end = time_str_to_minutes(section["end"])

    # handle "All Day" preference
    pref_start = 420 if prefs[day]["start"] == "All Day" else time_str_to_minutes(prefs[day]["start"])
    pref_end = 1320 if prefs[day]["end"] == "All Day" else time_str_to_minutes(prefs[day]["end"])

    return start >= pref_start and end <= pref_end

def has_time_conflict(sections):
    # Convert all sections into blocks of (dat, start_min, end_min)
    schedule = []
    for s in sections:
        day = s["day"]
        start = time_str_to_minutes(s["start"])
        end = time_str_to_minutes(s["end"])
        for existing in schedule:
            if existing["day"] == day and not (end <= existing["start"] or start >= existing["end"]):
                return True
        schedule.append({"day": day, "start": start, "end": end})
    return False

def generate_schedule(course_list, time_prefs):
    # Get all section combinations
    sections_options = [MOCK_SECTIONS.get(course, []) for course in course_list]
    all_combos = product(*sections_options)

    valid_schedules = []
    for combo in all_combos:
        if has_time_conflict(combo):
            continue
        if all(is_within_preference(section, time_prefs) for section in combo):
            schedule = {course_list[i]: combo[i] for i in range(len(course_list))}
            valid_schedules.append(schedule)
    return {"schedules": valid_schedules}