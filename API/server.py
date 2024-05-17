from flask import Flask, jsonify, render_template, request, redirect
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

# Function to initialize the database
def initialize_database():
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS profiles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fbSerialNo TEXT, screenName TEXT, firstName TEXT,
                 lastName TEXT, email TEXT, weight REAL, height REAL, gender TEXT,
                 dateOfBirth DATE, dailyGoal INTEGER)''')
    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

def fetch_all_profiles_from_db():
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM profiles")
    profiles_data = c.fetchall()
    conn.close()
    return profiles_data

def clear_all_profiles_from_db():
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute("DELETE FROM profiles")
    conn.commit()
    conn.close()

# Function to insert a new profile into the database
def insert_profile_to_db(profile_data):
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute("INSERT INTO profiles (fbSerialNo, screenName, firstName, lastName, email, weight, height, gender, dateOfBirth, dailyGoal) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (profile_data['fbSerialNo'], profile_data['screenName'], profile_data['firstName'], profile_data['lastName'], profile_data['email'], profile_data['weight'], profile_data['height'], profile_data['gender'], profile_data['dateOfBirth'], profile_data['dailyGoal']))
    conn.commit()
    conn.close()

# Route to delete all profiles from the database
#@app.route('/v1.0/clear', methods=["GET"])
#def clear_profiles():
    # Delete all profiles from the database
#    clear_all_profiles_from_db()
#    return jsonify({"message": "All profiles deleted from the database"})

@app.route('/v1.0/profiles', methods=["GET"])
def list_profiles():
    # Fetch all profiles from the database
    profiles_data = fetch_all_profiles_from_db()
    profiles_list = []
    # Construct a list of profiles from fetched data
    for profile_data in profiles_data:
        profile = {
            "id": profile_data[0],
            "fbSerialNo": profile_data[1],
            "screenName": profile_data[2],
            "firstName": profile_data[3],
            "lastName": profile_data[4],
            "email": profile_data[5],
            "weight": profile_data[6],
            "height": profile_data[7],
            "gender": profile_data[8],
            "dateOfBirth": profile_data[9],
            "dailyGoal": profile_data[10]
        }
        profiles_list.append(profile)
    return jsonify(profiles_list)


@app.route('/v1.0/device/imprint', methods=["POST"])
def imprint():
    if request.method == 'POST':
        # Extract profile data from the request
        serial_no = request.json.get('serialNo')
        # Check if the 'serialNo' field exists in the profile data
        if not serial_no:
            return jsonify({'error': 'Serial number not provided'}), 400


        conn = sqlite3.connect('profiles.db')
        c = conn.cursor()
        c.execute("SELECT * FROM profiles WHERE fbSerialNo = ?", (serial_no,))
        existing_profile = c.fetchone()
        conn.close()
        profile_data = {}
        #print(existing_profile)
        if existing_profile:
            # Replace missing fields with corresponding values from the database
            profile_data['userDeviceId'] = existing_profile[1]
            profile_data['din'] = existing_profile[1]
            profile_data['udi'] = existing_profile[1]
            profile_data['serialNo'] = existing_profile[1]

            # Add missing static fields to the response
            profile_data['deviceName'] = "FuelBand"
            profile_data['deviceString'] = "FuelBand"
            profile_data['color'] = "BLACK"
            profile_data['firmwareVersion'] = "A0.46.2296a"
            profile_data['softwareVersion'] = "A0.46.2296a"
            profile_data['carrier'] = "telecom"

        # Return the profile data as the response
        return jsonify(profile_data), 200
    else:
        return jsonify({'error': 'Method not allowed'}), 405  # Return 405 Method Not Allowed if not a POST request




@app.route('/v1.0/device/onetimetoken', methods=["GET"])
def onetimetoken():
    data = {"onetimetoken": "ABCDEF"}
    return jsonify(data)


events = []


@app.route('/plus/setup/ABCDEF', methods=["GET"])
def setup():
    global events
    print("Injecting setup complete event...")
    events.append({"status": "success",
                   "id": "setup",
                   "eventType": "setup_complete",
                   "payload": "{\"dailyGoal\": 2000.0, \"nextDailyGoal\": 2000.0, \"band_name\": \"FuelBand\"}"})
    return "Injecting setup complete event..."


#@app.route('/events/connect/42424242424242', methods=["GET"])
@app.route('/events/connect/<id>', methods=["GET"])
def get_events(id):
    global events
    print("Received ID:", id)
    print("Sending events:", events)
    data = {"status": "success", "events": events}
    return jsonify(data)


@app.route('/events/connect/<fbid>/ack/<id>', methods=["POST"])
def ack_events(id,fbid):
    print(request)
    print("request POST data:", request.get_json())
    global events
    events = list(filter(lambda e: e["id"] != id, events))
    print("sending acked events: ", events)
    data = {"status": "success", "events": events}
    return jsonify(data)


@app.route('/map/getAccessToken', methods=["GET"])
def accesstoken():
    data = {"access_token": "accesstoken",
            "expires_in": "10000000",
            "refresh_token": "refreshtoken"}
    return jsonify(data)


@app.route('/plus/v1.0/remotelogs/email', methods=["POST"])
def email():
    return "OK"


@app.route('/v1.0/me/profile', methods=["GET"])
def profile():
    data = {"success": "true",
            "screenName": "fuelband",
            "firstName": "fuelband",
            "lastName": "",
            "email": "x@example.com",
            "weight": 170.0,
            "height": 68.0,
            "gender": "male",
            "dateOfBirth": 315619200000,
            "dailyGoal": 2000.0,
            "pin": "",
            "deviceList": [{'deviceString': "FuelBand", 'deviceType': 'FUELBAND'}]}
    return jsonify(data)

@app.route('/v1.0/me/challenge/dailygoal/list', methods=["GET"])
def daily_goal():
    startTime = None
    endTime = None
    if not request.args.get("startTime").isdigit():
        startTime = int(datetime.now().timestamp())
    elif not request.args.get("endTime").isdigit():
        endTime = int((datetime.now() + timedelta(days=1)).timestamp())
    else:
        startTime = int(request.args.get("startTime"))
        endTime = int(request.args.get("endTime"))

    startTime = int(datetime.now().timestamp() * 1000)
    print(startTime)
    data = {"success": "true",
            "dailyGoalList": [{"challengeId": "CHALLENGE", "startTime": startTime, "endTime": endTime, "targetValue": 2000.0}]
            }
    return jsonify(data)


@app.route('/v1.0/me/activities/summary/daily/<day>', methods=["GET"])
def daily_summary(day):
    data = {"success": "true",
            "summary": {}}
    return jsonify(data)


@app.route('/v1.0/me/device/<id>', methods=["GET", "PUT"])
def device_info(id):
    data = {"success": "true",
            "din": id,
            "serialNumber": id,
            "deviceType": "FUELBAND",
            "deviceSring": "FuelBand"}
    return jsonify(data)

@app.route('/v1.0/me/device/<id>/settings', methods=["GET"])
def device_prefs(id):
    data = {"success": "true",
            "preference": {
                "FUELBANDSTEPS": 1234,
                "FUELBANDCALORIES": 1000,
                "FUELBANDFUEL": 4321,   
                "FUELBANDISLEFTORIENTATION": 0,   
            }}
    return jsonify(data)


@app.route('/me/account', methods=["GET"])
def account():
    data = {"success": "true",
            "entity": {"firstName": "fuelband",
                       "heightUnit": "in",
                       "weightUnit": "lb"},
            "firstName": "fuelband",
            "heightUnit": "in",
            "weightUnit": "lb"}
    return jsonify(data)


@app.route('/v1.0/me/sync/lasttimestamp', methods=["GET"])
def sync_params():
    data = {"success": "true",
            "upmid": "UPMID",
            "plusid": "PLSUID",
            "lastSyncOffset": 0,
            "lastSyncTimeStamp": 0}
    return jsonify(data)


@app.route('/v1.0/me/challenge', methods=["POST"])
def challenge():
    data = {"success": "true",
            "result": "success",
            "challengeId": "CHALLENGE",
            "challengeType": request.get_json()["challengeType"],
            "dailyGoalDate": request.get_json()["dailyGoalDate"],
            "dstOffset": request.get_json()["dstOffset"],
            "targetValue": request.get_json()["targetValue"],
            "tzOffset": request.get_json()["tzOffset"]}
    return jsonify(data)


# TODO
# GET Important to allow data to be cleared before timestamp.
"/v1.0/me/sync/lasttimestamp"
# POST sync data.
"/v2.0/me/sync"

@app.route('/<path:path>', methods=["GET", "POST", "PUT"])
def catch_all(path):
    print("PATH:", path)
    print("DATA:", request.get_json())
    data = {"success": "true",
            "result": "success"}
    return jsonify(data)

@app.route('/setup', methods=['GET', 'POST'])
def setup_profile():
    if request.method == 'POST':
        fbSerialNo = request.form['fbSerialNo']
        screenName = request.form['screenName']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        gender = request.form['gender']
        dateOfBirth = request.form['dateOfBirth']
        dailyGoal = int(request.form['dailyGoal'])

        # Write profile data to database
        conn = sqlite3.connect('profiles.db')
        c = conn.cursor()
        c.execute("INSERT INTO profiles (fbSerialNo, screenName, firstName, lastName, email, weight, height, gender, dateOfBirth, dailyGoal) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (fbSerialNo, screenName, firstName, lastName, email, weight, height, gender, dateOfBirth, dailyGoal))
        conn.commit()
        conn.close()

        return redirect('/success')  # Redirect to a success page after form submission
    else:
        return render_template('setup.html')

@app.route('/success')
def success():
    return "Profile setup successful!"

@app.route('/hid')
def hid():
    return render_template('index-hid.html')

@app.route('/v1.0/profile/input', methods=["GET", "POST"])
def input_profile():
    if request.method == "POST":
        # Extract form data
        profile_data = {
            'fbSerialNo': request.form['fbSerialNo'],
            'screenName': request.form['screenName'],
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'email': request.form['email'],
            'weight': float(request.form['weight']),
            'height': float(request.form['height']),
            'gender': request.form['gender'],
            'dateOfBirth': request.form['dateOfBirth'],
            'dailyGoal': float(request.form['dailyGoal'])
        }
        # Insert profile into the database
        insert_profile_to_db(profile_data)
        return redirect('/v1.0/profiles')  # Redirect to profile listing page after submission
    else:
        # Render the profile input form
        return render_template('profile_input_form.html')

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=5000)