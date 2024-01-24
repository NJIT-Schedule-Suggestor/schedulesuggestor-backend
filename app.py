from flask import Flask, jsonify
import os
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from retrieveCourses import retrieve_courses

# from generateSchedule import generate_Schedule


app = Flask(__name__)
CORS(app)
load_dotenv()
sql_password = os.environ.get("sqlpass")

# app.config["MYSQL_USER"] = "root"
# app.config["MYSQL_PASSWORD"] = sql_password
# app.config["MYSQL_HOST"] = "localhost"
# app.config["MYSQL_DB"] = "schedule_suggestor"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["MYSQL_USER"] = "zk61pnc0vuvwvfdh"
app.config["MYSQL_PASSWORD"] = sql_password
app.config["MYSQL_HOST"] = "g84t6zfpijzwx08q.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
app.config["MYSQL_DB"] = "pqx4tjcnq0ee8v05"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/")
def index():
    return "Schedule Suggestor"


@app.route("/courses/<course_name>")
def courses(course_name):
    # Use the courses function from retrieveCourses
    result = retrieve_courses(course_name, mysql)

    return jsonify(result)


# @app.route("/generate/")
# def generateSchedule():
#     result = generate_Schedule()

#     return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
