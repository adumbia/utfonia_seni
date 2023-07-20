from flask import Flask, render_template, request, jsonify
import requests
import datetime

app = Flask(__name__)

FHIR_SERVER_BASE_URL = "https://hapi.fhir.org/baseR4/"
PATIENT_ENDPOINT = "Patient"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/filtered_patients")
def filtered_patients():
    min_age = int(request.args.get("min_age", 0))
    max_age = int(request.args.get("max_age", 1000))

    # Fetch FHIR resources from the server
    url = f"{FHIR_SERVER_BASE_URL}{PATIENT_ENDPOINT}"
    response = requests.get(url)

    if response.status_code == 200:
        patients = response.json()
        filtered_patients = filter_patients_by_age(patients, min_age, max_age)
        return jsonify(filtered_patients)
    else:
        return jsonify({"error": "Failed to fetch FHIR resources."})

def filter_patients_by_age(patients, min_age, max_age):
    today = datetime.date.today()

    filtered_patients = []
    for patient in patients:
        birth_date_str = patient["birthDate"]
        birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        age = (today - birth_date).days // 365  # Calculate age in years
        if min_age <= age <= max_age:
            filtered_patients.append(patient)

    return filtered_patients

if __name__ == "__main__":
    app.run(debug=True)