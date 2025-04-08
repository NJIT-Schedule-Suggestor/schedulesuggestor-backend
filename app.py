from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from retrieveCourses import retrieve_courses
from generateSchedule import generate_schedule

app = Flask(__name__)
CORS(app)  # works since frontend is on same host

# MySQL config
# zaids config:
# app.config["MYSQL_USER"] = "zk61pnc0vuvwvfdh"
# app.config["MYSQL_PASSWORD"] = sql_password
# app.config["MYSQL_HOST"] = "g84t6zfpijzwx08q.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
# app.config["MYSQL_DB"] = "pqx4tjcnq0ee8v05"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# local config:
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "2002"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_DB"] = "schedule_suggestor"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    return "Schedule Suggestor"

@app.route("/courses")
def all_courses():
    result = retrieve_courses(None, mysql)
    return jsonify(result)

@app.route("/courses/<course_name>")
def courses(course_name):
    result = retrieve_courses(course_name, mysql)
    return jsonify(result)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)
        selected_courses = data.get("selectedCourses", [])
        time_preferences = data.get("timePreferences", {})

        print("Selected:", selected_courses)
        print("Prefs:", time_preferences)


        result = generate_schedule(selected_courses, time_preferences)
        return jsonify(result)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)