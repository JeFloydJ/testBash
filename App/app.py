# Import necessary modules
import zipfile
from flask import Flask, request, render_template, redirect, jsonify, send_file
import logging
import requests
import csv
import urllib.parse
from dotenv import load_dotenv
from auth.authAltru import authAltru
from auth.authSalesforce import authSalesforce
from Events.eventReportData import ReportProcessor
from Events.eventTransferDataOrganizations import Adapter
import subprocess
import os
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#absolute path of files
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "App", "{}")

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    force=True)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Define client IDs
client_ids = {
    'salesforce': os.getenv("CLIENT_ID_SALESFORCE"),
    'altru': os.getenv("CLIENT_ID_SKY_API")
}

# Define client secrets
client_secrets = {
    'salesforce': os.getenv("CLIENT_SECRET_SALESFORCE"),
    'altru': os.getenv("CLIENT_SECRET_SKY_API")
}

# Define redirect URIs
redirect_uris = {
    'skyapi': os.getenv("REDIRECT_URI_SKY_API"),
    'salesforce': os.getenv("REDIRECT_URI_SALESFORCE")
}

# Define token URLs
token_urls = {
    'salesforce': 'https://login.salesforce.com/services/oauth2/token',
    'altru': 'https://oauth2.sky.blackbaud.com/token'
}

# List of files with tokens
token_files = ['altru_token.txt', 'altru_refresh_token.txt', 'salesforce_token.txt', 'salesforce_refresh_token.txt', 'salesforce_instance.txt', 'data.txt', 'finish.txt']

reports_of_sent_data = ["contacts_response", 
                     "organizations_address_update_response", 
                     "organizations_response",
                     "housolds_response",
                     "organizations_phone_response",
                     "organizations_address_response",       
                     "organizations_phone_update_response"]

#List of reports and csv files
#special_files = ['Veevart Organization Addresses Report test_output.csv', 'Veevart Organization Addresses Report test_response.json', 'Veevart Organization Phones Report test_output.csv', 'Veevart Organization Phones Report test_response.json', 'Veevart Organizations Report test_output.csv', 'Veevart Organizations Report test_response.json', 'Veevart HouseHolds Report test_response.json', 'Veevart HouseHolds Report test_output.csv', 'Veevart Contacts Report test_response.json', 'Veevart Contacts Report test_output.csv', 'Veevart Contacts Report Phones test_response.json', 'Veevart Contacts Report Phones test_output.csv', 'Veevart Contacts Report Email test_response.json', 'Veevart Contacts Report Email test_output.csv', 'Veevart Contacts Report Address test_response.json', 'Veevart Contacts Report Address test_output.csv']

# delete the content in each token file 
for filename in token_files:
    save_path_files = os.path.join(ABS_PATH.format(''), filename)
    open(save_path_files, 'w').close()

#delete content in each csv and json file
# for filename in special_files:
#     open((ABS_PATH.format(f'Events/{filename}')), 'w').close()


#parameters: file of text
#description: verify if the file is empty
#return: if the file is empty or not.
def isEmpty(file):
    return not bool(file.read())

#parameters: 
#description: generate report of data submitted
#return: 
@app.route('/generateReport', methods=['GET'])
def generateReport():
    all_csv_paths = []

    for report in reports_of_sent_data:
        txt_path = ABS_PATH.format(f'logs/{report}.txt')
        json_path = ABS_PATH.format(f'logs/{report}.json')
        csv_path = ABS_PATH.format(f'reports/{report}.csv')
        
        processor = ReportProcessor(txt_path, json_path, csv_path)
        
        processor.convert_to_json()
        
        processor.generate_report_send_data(report)
        
        all_csv_paths.append(csv_path)

    zip_file_path = os.path.join(os.path.dirname(csv_path), 'reports.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        for csv_path in all_csv_paths:
            zip_file.write(csv_path, os.path.basename(csv_path))

    return send_file(zip_file_path, as_attachment=True)

#parameters: 
#description: verify if the process to sent data is finished
#return: status of process to sent data
@app.route('/Validator') 
def validateToken():
    try:
        # Check if the finish file exists
        finish_path = ABS_PATH.format('finish.txt')
        if os.path.exists(finish_path):
            return jsonify({'status': 200})

        # Check if the error file exists
        error_path = ABS_PATH.format('error.txt')
        if os.path.exists(error_path):
            with open(error_path, 'r') as f:
                error_message = f.read()
            return jsonify({'status': 'error', 'message': error_message})
        
        # If neither file exists, the process is still running
        return jsonify({'status': 'in_progress'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

#parameters: 
#description: add csv files to project 
#return: store csv files
@app.route('/upload', methods=["POST"])
def upload():
    if request.method == 'POST':
        if request.files:
            uploaded_files = request.files.getlist("filename")
            for file in uploaded_files:
                save_path = os.path.join(ABS_PATH.format('data'), f'{file.filename}')
                file.save(save_path)
                with open(save_path, 'r') as f:
                    csv_file = csv.reader(f)
            try:
                save_data_path = os.path.join(ABS_PATH.format(''), 'data.txt')
                with open(save_data_path, 'w') as f:
                    f.write('data subida')
            except Exception as e:
                logger.error(f"Error writing to file: {e}")
            return jsonify({'message': 'Successfully saved', 'success': True})
    return redirect('/')

#parameters: 
#description: delete csv files
#return: csv files deleted
@app.route('/delete', methods=["POST"])
def delete():
    save_path = os.path.join(ABS_PATH.format('/data'), '*.csv')
    files = glob.glob(save_path)
    for file_name in files:
        os.remove(file_name)
    return jsonify({'message': 'files deleted', 'success': True})


#parameters: 
#description: the main page of this project, decided wich page render depends of the auths
#return: render the page
@app.route('/')
def index():
 
    loggedSalesforce = False
    awsData = False
    transferData = False
    transferPage = False
    
    with open(ABS_PATH.format('salesforce_token.txt'), 'r') as f:
        if not isEmpty(f):
            loggedSalesforce = True 

    # Si está conectado a Sky Api, la variable es True
    # with open(ABS_PATH.format('altru_token.txt'), 'r') as f:
    #     if not isEmpty(f):
    #         loggedSkyApi = True

    with open(ABS_PATH.format('data.txt'), 'r') as f:
        if not isEmpty(f):
            awsData = True 

    with open(ABS_PATH.format('finish.txt'), 'r') as f:
        if not isEmpty(f):
            transferData = True

    if loggedSalesforce and awsData:
        transferPage = True
 
    # Render the index page
    return render_template('index.html', transferPage=transferPage, loggedSalesforce=loggedSalesforce, transferData=transferData, awsData=awsData)

#parameters: 
#description: get data in sky api, after transfer to salesforce
#return: render the page of the complete data
@app.route('/transferData', methods=['GET'])
def transferData():

    script_path = ABS_PATH.format('transferProcess.py')

    subprocess.Popen(['python3', script_path, '&'])

    return {'status': 200}

#parameters: 
#description: obtain access tokens when authorizing in salesforce
#return: render the page
@app.route('/salesforce/callback')
def getSalesforceToken():
    # Define the service and API
    service = 'salesforce'
    api = 'salesforce'
    # Parse the URL query
    query = urllib.parse.urlparse(request.url).query
    query_components = dict(qc.split("=") for qc in query.split("&") if "=" in qc)

    # If the query contains a code, get the token
    if "code" in query_components:
        code = query_components["code"]
        access_token = query_components["code"]
        access_token = access_token.replace("%3D%3D", "==")

        # Write the access token to a file
        with open(f'{service}_token.txt', 'w') as f:
            f.write(access_token)
        logger.info(access_token)
        # Request an access token
        token_url = "https://login.salesforce.com/services/oauth2/token"
        token_data = {
            "grant_type": "authorization_code",
            "code": access_token,
            "redirect_uri": redirect_uris[api],
            "client_id": client_ids[service],
            "client_secret": client_secrets[service]
        }
        token_response = requests.post(token_url, data=token_data)
        #logger.info(token_response)
        logger.info(token_response)
        # If the token response is successful, write the tokens to files
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            refresh_token = token_response.json()["refresh_token"]
            instance = token_response.json()["instance_url"]
            logger.info(instance)
            try:
                save_path_access = os.path.join(ABS_PATH.format(''), f'{service}_token.txt')
                with open(save_path_access, 'w') as f:
                    f.write(access_token)
                save_path_refresh = os.path.join(ABS_PATH.format(''), f'{service}_refresh_token.txt')
                with open(save_path_refresh, 'w') as f:
                    f.write(refresh_token)
                save_path_instance = os.path.join(ABS_PATH.format(''), f'{service}_instance.txt')
                with open(save_path_instance, 'w') as f:
                    f.write(instance)
            except Exception as e:
                logger.error(f"Error writing tokens to file: {e}")
        else:
            logger.warning(f"Token response error: {token_response.content}")
    
    #logger.info(ans)

    # Return the answer
    return redirect('/')

#parameters: service (others CRM)
#description: obtain method for service
#return: render the page oh service
@app.route('/auth/<service>', methods=['GET'])
def auth(service):
    if service == 'altru':
        auth_url = authAltru()
    elif service == 'salesforce':
        auth_url = authSalesforce()
    return redirect(auth_url)


#run the server in port 8000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
