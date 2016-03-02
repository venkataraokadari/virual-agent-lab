import os, requests, json, string, datetime, csv
import randr, nlc

# ------------------------------------------------
# GLOBAL VARIABLES (Set from ENV Variables)-------
# Dialog and classifier
# -- defaults for testing
DIALOG_ID = 'xxxx'
DIALOG_USERNAME = 'xxxx'
DIALOG_PASSWORD = 'xxxx'
# -- overwrites by env variables
if 'DIALOG_ID' in os.environ:
    DIALOG_ID = os.environ['DIALOG_ID']
if 'VCAP_SERVICES' in os.environ:
    dialog = json.loads(os.environ['VCAP_SERVICES'])['dialog'][0]
    DIALOG_USERNAME = dialog["credentials"]["username"]
    DIALOG_PASSWORD = dialog["credentials"]["password"]

#Dialog Functions
def BMIX_get_first_dialog_response_json():
    global DIALOG_ID, DIALOG_USERNAME, DIALOG_PASSWORD
    #print 'in first_dialog'
    POST_SUCCESS = 201
    response_json = None
    url = 'https://watson-api-explorer.mybluemix.net/dialog/api/v1/dialogs/' + DIALOG_ID + '/conversation'
    r = requests.post(url, auth=(DIALOG_USERNAME, DIALOG_PASSWORD))
    if r.status_code == POST_SUCCESS:
        response_json = r.json()
        response_json['response'] = format_dialog_response_as_string(response_json['response'])
        #print response_json
    return response_json

def BMIX_get_next_dialog_response(client_id, conversation_id, input):
    global DIALOG_ID, DIALOG_USERNAME, DIALOG_PASSWORD
    print 'in second dialog'
    POST_SUCCESS = 201
    response = ''
    url = 'https://watson-api-explorer.mybluemix.net/dialog/api/v1/dialogs/' + DIALOG_ID + '/conversation'
    payload = {'client_id': client_id, 'conversation_id': conversation_id, 'input': input}
    r = requests.post(url, auth=(DIALOG_USERNAME, DIALOG_PASSWORD), params=payload)
    print("DIALOG NEXT RESPONSE")
    print(r.status_code)
    print(r)
    if r.status_code == POST_SUCCESS:
        response = format_dialog_response_as_string(r.json()['response'])
    return response

def format_dialog_response_as_string(response_strings):
    response = ''
    if response_strings:
        for response_string in response_strings:
            if str(response_string) != '':
                if len(response) > 0:
                    response = response + '<BR>' + response_string
                else:
                    response = response_string
    return response
