def retrieve_courses(course_name, mysql):
    course_name = str(course_name.upper())
    cur = mysql.connection.cursor()

    # Get all Tables
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    table_names = [table["Tables_in_pqx4tjcnq0ee8v05"] for table in tables]

    course_dict = {}

    # Go through each table to get all classes
    for table_name in table_names:
        query = f"SELECT Course, Title, DeliveryMode, Credits FROM pqx4tjcnq0ee8v05.`{table_name}`"

        cur.execute(query)

        courses = cur.fetchall()

        # Filter by class we want
        for course in courses:
            course_key = course["Course"]
            if course_key.startswith(course_name):
                if course_key not in course_dict:
                    course_dict[course_key] = {
                        "Course": course_key,
                        "Title": course["Title"],
                        "Credits": course["Credits"],
                        "DeliveryModes": set(),
                    }
                course_dict[course_key]["DeliveryModes"].add(course["DeliveryMode"])

    # Get the final list format
    final_list = [
        {
            "Course": entry["Course"],
            "Title": entry["Title"],
            "Credits": entry["Credits"],
            "DeliveryModes": list(entry["DeliveryModes"]),
        }
        for entry in course_dict.values()
    ]

    return {"courses": final_list}
