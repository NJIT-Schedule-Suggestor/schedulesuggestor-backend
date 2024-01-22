# from flask_mysqldb import MySQL


def retrieve_courses(course_name, mysql):
    course_name = str(course_name.upper())
    cur = mysql.connection.cursor()

    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    table_names = [table["Tables_in_schedule_suggestor"] for table in tables]

    course_list = []

    for table_name in table_names:
        query = f"SELECT Course FROM schedule_suggestor.`{table_name}`"

        cur.execute(query)

        courses = cur.fetchall()

        filtered_courses = [
            course["Course"]
            for course in courses
            if course["Course"].startswith(course_name)
        ]

        course_list.extend(filtered_courses)

    final_list = sorted(set(course_list))

    return {"courses": final_list}
