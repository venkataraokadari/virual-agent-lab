import os, requests, json, string, datetime, csv

# ------------------------------------------------
# GLOBAL VARIABLES (Set from ENV Variables)-------
# Retrieve_and_rank
# -- defaults for testing
SOLR_CLUSTER_ID = 'xxxx'
RANKER_ID = 'xxxx'
RETRIEVE_AND_RANK_USERNAME = 'xxxx'
RETRIEVE_AND_RANK_PASSWORD = 'xxxx'
if 'SOLR_CLUSTER_ID' in os.environ:
    SOLR_CLUSTER_ID = os.environ['SOLR_CLUSTER_ID']
if 'RANKER_ID' in os.environ:
    RANKER_ID = os.environ['RANKER_ID']
if 'VCAP_SERVICES' in os.environ:
    retrieve_and_rank = json.loads(os.environ['VCAP_SERVICES'])['retrieve_and_rank'][0]
    RETRIEVE_AND_RANK_USERNAME = retrieve_and_rank["credentials"]["username"]
    RETRIEVE_AND_RANK_PASSWORD = retrieve_and_rank["credentials"]["password"]
# Externalized customizations --------------------
ISSUE_LOOKUP_MESSAGE = '[##Issue_Lookup##]'

# ------------------------------------------------
# FUNCTIONS --------------------------------------
# Encapsulate BMIX services plus helper funcs ----
def BMIX_retrieve_and_rank(args_string, fields_str):
    global SOLR_CLUSTER_ID, RANKER_ID, RETRIEVE_AND_RANK_USERNAME, RETRIEVE_AND_RANK_PASSWORD
    POST_SUCCESS = 200
    docs = []
    url = 'https://gateway.watsonplatform.net/retrieve-and-rank/api/v1/solr_clusters/' + SOLR_CLUSTER_ID + '/solr/gemstone-collection3/select?q=' + args_string + '&wt=json&fl=' + fields_str
    r = requests.get(url, auth=(RETRIEVE_AND_RANK_USERNAME, RETRIEVE_AND_RANK_PASSWORD), headers={'content-type': 'application/json'})
    if r.status_code == POST_SUCCESS:
        #parse rr response
        report_title_1 = parse_rr_output(r,0,'report_title')
        defect_status_1 = parse_rr_output(r,0,'defect_status')
        text_description_1 = parse_rr_output(r,0,'text_notes')
        report_title_2 = parse_rr_output(r,1,'report_title')
        defect_status_2 = parse_rr_output(r,1,'defect_status')
        text_description_2 = parse_rr_output(r,1,'text_notes')
        report_title_3 = parse_rr_output(r,2,'report_title')
        defect_status_3 = parse_rr_output(r,2,'defect_status')
        text_description_3 = parse_rr_output(r,2,'text_notes')
        docs = '<b>Incident: </b>' + report_title_1 + '<br><b>Status: </b>' + defect_status_1 + '<br><b>Description: </b>' + text_description_1 + '<br><br><b>Incident: </b>' + report_title_2 + '<br><b>Status: </b>' +  defect_status_2 + '<br><b>Description: </b>' + text_description_2 + '<br><br><b>Incident: </b> ' + report_title_3 + '<br><b>Status: </b>' + defect_status_3 + '<br><b>Description: </b>' + text_description_3
    else:
        docs = '500 error connecting with Retrieve and Rank service'
    return docs

def issue_lookup(response, question):
    docs = BMIX_retrieve_and_rank(question, 'report_title,text_notes,defect_status')
    if (len(docs) > 0):
        application_response = docs
    return application_response

def issue_lookup_requested(response):
    global ISSUE_LOOKUP_MESSAGE
    if (response == ISSUE_LOOKUP_MESSAGE):
        return True
    return False

def parse_rr_output(r, field, depth):
    answer = json.dumps(r.json()['response']['docs'][depth][field])
    answer = answer.translate(None,'\[\]\"')
    if (len(answer) > 400):
        answer = answer[0:400]+'...'
    return answer

def get_application_response(response, question):
    application_response = response
    if (issue_lookup_requested(response)):
        application_response = issue_lookup(application_response, question)
    return application_response
