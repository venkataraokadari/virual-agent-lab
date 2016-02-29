import os, requests, json, string, datetime, csv

# ------------------------------------------------
# GLOBAL VARIABLES (Set from ENV Variables)-------
# Dialog and classifier
# -- defaults for testing
CLASSIFIER_ID = 'xxxx'
CLASSIFIER_USERNAME = 'xxxx'
CLASSIFIER_PASSWORD = 'xxxx'
# -- overwrites by env variables
if 'CLASSIFIER_ID' in os.environ:
    CLASSIFIER_ID = os.environ['CLASSIFIER_ID']
if 'VCAP_SERVICES' in os.environ:
    natural_language_classifier = json.loads(os.environ['VCAP_SERVICES'])['natural_language_classifier'][0]
    CLASSIFIER_USERNAME = natural_language_classifier["credentials"]["username"]
    CLASSIFIER_PASSWORD = natural_language_classifier["credentials"]["password"]

#NLC Functions
def BMIX_get_class_name(question, threshold):
    global CLASSIFIER_ID, CLASSIFIER_USERNAME, CLASSIFIER_PASSWORD
    POST_SUCCESS = 200
    class_name = ''
    url = 'https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/' + CLASSIFIER_ID + '/classify'
    r = requests.post(url, auth=(CLASSIFIER_USERNAME, CLASSIFIER_PASSWORD), headers={'content-type': 'application/json'}, data=json.dumps({'text': question}))

    if r.status_code == POST_SUCCESS:
        classes = r.json()['classes']
        if len(classes) > 0:
            confidence = classes[0]['confidence']
            if (confidence > threshold):
                class_name = classes[0]['class_name']
    return class_name

def formulate_classified_question(class_name, question):
    prefix = ''
    if class_name != '':
        prefix = '[##' + class_name + '##] '
    return  prefix + question
