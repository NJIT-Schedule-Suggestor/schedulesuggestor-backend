from datetime import datetime, timedelta
from itertools import product
from collections import defaultdict

# filter out comboos with time conflicts, and violations of time preferences
# return clean JSON with each valid schedule


def time_str_to_minutes(t):
    # convert time string into minutes since midnight
    # ex. "2:30 PM" becomes 14 * 60 + 30 = 870
    # ex. "11:00 AM" becomes 11 * 60 + 0 = 660
    dt = datetime.strptime(t, "%I:%M %p")
    return dt.hour * 60 + dt.minute

def get_sections_for_courses(course_list, mysql):
    # get sections for each course in course_list
    if not course_list:
        return {}
    
    cur = mysql.connection.cursor()

    # format for SQL IN clause
    format_str = ','.join(['%s'] * len(course_list))

    # step 1: fetch sections
    cur.execute(f"""
        SELECT
            cs.id as section_id,
            cs.course_code,
            cs.section,
            cs.mode,
            cs.title,
            cs.credits,
            sm.day_of_week,
            TIME_FORMAT(sm.start_time, '%%l:%%i %%p') as start,
            TIME_FORMAT(sm.end_time, '%%l:%%i %%p') as end
        FROM CourseSections cs
        JOIN SectionMeetings sm ON cs.id = sm.section_id
        WHERE cs.course_code IN ({format_str})
        ORDER BY cs.course_code, cs.section, sm.day_of_week
    """, course_list)

    results = cur.fetchall()

    # step 2: organize results by course_code
    section_map = defaultdict(list)
    seen_sections = {}

    for row in results:
        key = (row['course_code'], row['section'])

        if key not in seen_sections:
            seen_sections[key] = {
                "section": row['section'],
                "mode": row['mode'],
                "title": row['title'],
                "credits": row['credits'],
                "meetings": []
            }

        seen_sections[key]["meetings"].append({
            "day": row['day_of_week'],
            "start": row['start'],
            "end": row['end']
        })

    # step 3: convert seen_sections to final structure
    for (course_code, _), section in seen_sections.items():
        section_map[course_code].append(section)
    
    return section_map
      
def is_within_preference(section, prefs):
    meetings = section.get("meetings", [section])  # fallback to flat sections
    for m in meetings:
        day = m["day"]
        if day not in prefs:
            return False
        start = time_str_to_minutes(m["start"])
        end = time_str_to_minutes(m["end"])
        pref_start = 420 if prefs[day]["start"] == "All Day" else time_str_to_minutes(prefs[day]["start"])
        pref_end = 1320 if prefs[day]["end"] == "All Day" else time_str_to_minutes(prefs[day]["end"])
        if start < pref_start or end > pref_end:
            return False
    return True

def has_time_conflict(sections):
    schedule = []
    for section in sections:
        meetings = section.get("meetings", [section])  # fallback to flat sections
        for m in meetings:
            day = m["day"]
            start = time_str_to_minutes(m["start"])
            end = time_str_to_minutes(m["end"])
            for existing in schedule:
                if existing["day"] == day and not (end <= existing["start"] or start >= existing["end"]):
                    return True
            schedule.append({"day": day, "start": start, "end": end})
    return False

# def generate_schedule(course_list, time_prefs, mysql=None):
#     if mysql:
#         course_sections = get_sections_for_courses(course_list, mysql)
#     else:
#         # fallback to mock for testing
#         raise ValueError("Database connection is required in production")

#     sections_options = [course_sections.get(course, []) for course in course_list]
#     all_combos = product(*sections_options)

#     valid_schedules = []
#     for combo in all_combos:
#         if has_time_conflict(combo):
#             continue
#         if all(is_within_preference(section, time_prefs) for section in combo):
#             schedule = {course_list[i]: combo[i] for i in range(len(course_list))}
#             valid_schedules.append(schedule)
#     return {"schedules": valid_schedules}
def generate_schedule(selected_courses, time_preferences, mysql):
    cur = mysql.connection.cursor()

    # Fetch all valid meetings
    format_time = lambda t: (datetime.min + t).strftime("%I:%M %p") if isinstance(t, timedelta) else str(t)
    query = """
        SELECT cs.course_code, cs.section, cs.mode, cs.title, cs.credits,
               sm.day_of_week, sm.start_time, sm.end_time
        FROM CourseSections cs
        JOIN SectionMeetings sm ON cs.id = sm.section_id
        WHERE cs.course_code IN %s
    """
    cur.execute(query, (tuple(selected_courses),))
    raw = cur.fetchall()

    # Group by (course, section)
    from collections import defaultdict
    sections = defaultdict(lambda: {"meetings": []})

    for row in raw:
        key = (row["course_code"], row["section"])
        sections[key].update({
            "section": row["section"],
            "title": row["title"],
            "credits": float(row["credits"]),
        })
        sections[key]["meetings"].append({
            "day": row["day_of_week"],
            "start": format_time(row["start_time"]),
            "end": format_time(row["end_time"]),
        })

    # Pick first section per course (naive)
    schedule = {}
    for course in selected_courses:
        for (code, section), data in sections.items():
            if code == course:
                schedule[course] = data
                break

    return {"schedules": [schedule]}


