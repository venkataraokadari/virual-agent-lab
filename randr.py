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
    titles = []
    defects = []
    notes = []
    url = 'https://gateway.watsonplatform.net/retrieve-and-rank/api/v1/solr_clusters/' + SOLR_CLUSTER_ID + '/solr/virtual_agent_collection/select?q=' + args_string + '&wt=json&fl=' + fields_str
    r = requests.get(url, auth=(RETRIEVE_AND_RANK_USERNAME, RETRIEVE_AND_RANK_PASSWORD), headers={'content-type': 'application/json'})
    print r.json()
    if r.status_code == POST_SUCCESS:
        print 'in rr 200'
        #parse rr response
        for i in range(0,3):
            titles[i] = json.dumps(r.json()['response']['docs'][i]['report_title'])
            titles[i] = titles[i].translate(None,'\[\]\"')
        for j in range(0,3):
            defects[j] = json.dumps(r.json()['response']['docs'][j]['defect_status'])
            defects[j] = defects[j].translate(None,'\[\]\"')
        for k in range(0,3):
            notes[k] = json.dumps(r.json()['response']['docs'][k]['text_notes'])
            notes[k] = notes[k].translate(None,'\[\]\"')
        #format response
        docs = '<b>Incident: </b>' + titles[0] + '<br><b>Status: </b>' + defects[0] + '<br><b>Description: </b>' + notes[0] + '<br><br><b>Incident: </b>' + titles[1] + '<br><b>Status: </b>' +  defects[1] + '<br><b>Description: </b>' + notes[1] + '<br><br><b>Incident: </b> ' + titles[2] + '<br><b>Status: </b>' + defects[2] + '<br><b>Description: </b>' + notes[2]
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

def get_application_response(response, question):
    application_response = response
    if (issue_lookup_requested(response)):
        application_response = issue_lookup(application_response, question)
    return application_response
