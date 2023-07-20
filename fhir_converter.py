import hl7apy
from hl7apy.parser import parse_message, parse_segment, parse_field, parse_component
import fhir.resources
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.bundle import Bundle, BundleEntry
import datetime
from fhir.resources.identifier import Identifier
import json
import requests


def serialize_datetime(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def translate_gender(gender_code):
    if gender_code == 'M':
        return 'male'
    elif gender_code == 'F':
        return 'female'
    else:
        return 'unknown'


def hl7v2_to_fhir(hl7_message):
    # Parse the HLv2 message
    parsed_message = hl7apy.parser.parse_message(hl7_message, find_groups=True)

    # Extract relevant data from the parsed message
    patient_name = parsed_message.PID.PID_5.value
    dob_string = parsed_message.PID.PID_7.value
    dob_date = datetime.datetime.strptime(dob_string, "%Y%m%d")
    gender = parsed_message.PID.PID_8.value

    # Create FHIR Patient resource
    patient = Patient()
    patient.name = [HumanName(use="official", text=patient_name)]
    # Translate gender code
    patient.gender = translate_gender(gender)

    # Check if the date of birth is present
    if dob_string:
        patient.birthDate = dob_date

    # Generate an identifier for the patient
    patient.identifier = [Identifier(system="urn:example:patient-identifier", value="1111111111")]

    return patient


if __name__ == "__main__":
    msh = "MSH|^~\&|SendingApp|SendingFacility|HL7API|PKB|20160102101112||ADT^A01|ABC0000000001|P|2.5\r"
    pid = "PID|||1111111111^^^NHS^NH||Langworth^^Shaun^^Sir||19260508|M|||^11 Some St^London^Greater London^NE1 2CD^GBR||01234567890^PRN~07123456789^PRS|^NET^sl1792911892@gmail.com~01234567890^WPN||||||||||||||||N|\r"
    pv1 = "PV1|1|I|^^^^^^^My Ward||||^Jones^Stuart^James^^Dr^|^Smith^William^^^Dr^|^Foster^Terry^^^Mr^|||||||V00001|||||||||||||||||||||||||201508011000|201508011200\r"
    hl7_message = msh + pid + pv1
    patient = hl7v2_to_fhir(hl7_message)

    # Convert FHIR Patient resource to a dictionary
    patient_dict = patient.dict()

    # Print FHIR Patient resource in JSON format with custom serializer
    print(json.dumps(patient_dict, indent=2, default=serialize_datetime))
    patientjson = (json.dumps(patient_dict, indent=2, default=serialize_datetime))
    # Set the URL for the API call
    url = 'https://hapi.fhir.org/baseR4/Patient'

    # Make the API call using requests.post with JSON data in the request body
    response = requests.post(url, json=patientjson, headers={"Content-Type": "application/fhir+json"})

    # Check the response status code and handle accordingly
    if response.status_code == 200:
        print("API call successful.")
        print("Response data:")
        print(response.json())
    else:
        print(f"API call failed with status code: {response.status_code}")
