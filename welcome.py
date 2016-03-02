# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, requests, json, string, datetime
from flask import Flask, request, jsonify, render_template
import dialog, nlc, randr

# Externalized customizations --------------------
WATSON_IMAGE = 'watson.jpg'
#WATSON_STYLE = 'another'
WATSON_STYLE = 'chat-watson'
#HUMAN_STYLE = 'me'
HUMAN_STYLE = 'chat-human'
#CHAT_TEMPLATE = 'chat.html'
CHAT_TEMPLATE = 'IBM-style-dialog.html'
#QUESTION_INPUT = 'question'
QUESTION_INPUT = 'response-input'
#PERONA_STYLE
PERSONA = 'John'
PERSONA_IMAGE = 'watson.jpg'
# Reset conversation -----------------------------
DIALOG_CLIENT_ID = 0
DIALOG_CONVERSATION_ID = 0
POSTS = []

# ------------------------------------------------
# CLASSES ----------------------------------------
class Post:
    def __init__(self, style, icon, text, datetime, name):
        self.style = style
        self.icon = icon
        self.text = text
        self.datetime = datetime
        self.name = name

# UI - formatting chat window responses ----------
def post_watson_response(response):
    global WATSON_IMAGE, POSTS, HUMAN_STYLE, WATSON_STYLE
    now = datetime.datetime.now()
    post = Post(WATSON_STYLE, WATSON_IMAGE, response, now.strftime('%Y-%m-%d %H:%M'), 'Watson')
    POSTS.append(post)
    #print 'in post_watson_response'
    #print post
    return post

def post_user_input(input):
    global POSTS, HUMAN_STYLE, WATSON_STYLE, PERSONA_IMAGE, PERSONA
    now = datetime.datetime.now()
    post = Post(HUMAN_STYLE, PERSONA_IMAGE, input, now.strftime('%Y-%m-%d %H:%M'), PERSONA)
    POSTS.append(post)
    #print 'in post_user_input'
    return post

#Orchestration Function
def orchestrate(client_id, conversation_id, question):
    #Define NLC confidence threshold
    threshold = 0
    #print 'in orchestrate'
    #Classify question with Watson NLC service
    class_name = BMIX_get_class_name(question, threshold)
    #Format question for dialog calling "handshake" formatter
    classified_question = formulate_classified_question(class_name, question)
    #Invoke Watson Dialog service - classified_question (with prepended class_name) passed
    response = BMIX_get_next_dialog_response(client_id, conversation_id, classified_question)
    #Intercept Dialog service response for supplemental service calls
    application_response = get_application_response(response, question)
    return application_response

# Functions in external modules ------------------
get_application_response = randr.get_application_response
BMIX_get_class_name = nlc.BMIX_get_class_name
formulate_classified_question = nlc.formulate_classified_question
BMIX_get_first_dialog_response_json = dialog.BMIX_get_first_dialog_response_json
BMIX_get_next_dialog_response = dialog.BMIX_get_next_dialog_response

app = Flask(__name__)

@app.route('/')
def Index():
    global POSTS, CHAT_TEMPLATE, DIALOG_CLIENT_ID, DIALOG_CONVERSATION_ID
    POSTS = []
    #print 'in get'
    first_response = ''
    response_json = BMIX_get_first_dialog_response_json()
    if response_json != None:
        DIALOG_CLIENT_ID = response_json['client_id']
        DIALOG_CONVERSATION_ID = response_json['conversation_id']
        response = response_json['response']
        #print DIALOG_CLIENT_ID
        #print DIALOG_CONVERSATION_ID
        #print response
    post_watson_response(response)
    return render_template(CHAT_TEMPLATE, posts=POSTS)

@app.route('/', methods=['POST'])
def Index_Post():
    global POSTS, CHAT_TEMPLATE, QUESTION_INPUT, DIALOG_CLIENT_ID, DIALOG_CONVERSATION_ID
    #print 'in post'
    question = request.form[QUESTION_INPUT]
    #print question
#    Display original question
    post_user_input(question)
#    Orchestrate
    application_response = orchestrate(DIALOG_CLIENT_ID, DIALOG_CONVERSATION_ID, question)
#    Display application_response
    post_watson_response(application_response)
    return render_template(CHAT_TEMPLATE, posts=POSTS)

@app.route('/service/')
def Service():
    response_json = BMIX_get_first_dialog_response_json()
    if response_json != None:
        DIALOG_CLIENT_ID = response_json['client_id']
        DIALOG_CONVERSATION_ID = response_json['conversation_id']
    return json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ': '))

@app.route('/service/', methods=['POST'])
def Service_Post():
    global POSTS, CHAT_TEMPLATE, QUESTION_INPUT
    data = json.loads(request.data)
    client_id = data['client_id']
    conversation_id = data['conversation_id']
    question = data['question']
#    Orchestrate
    application_response = orchestrate(client_id, conversation_id, question)
    return (application_response)

@app.route('/slack/', methods=['POST'])
def Slack_Post():
    return ('{"text": "Hello world from Watson dialog"}')

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(port))
