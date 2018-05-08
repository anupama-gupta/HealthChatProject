from __future__ import print_function # Python 2/3 compatibility
import json
import datetime
import time
import os
import dateutil.parser
import logging
import decimal
import uuid
from urllib.request import urlopen


from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import config


config.setup_examples()
import infermedica_api

import traceback

# --- Helpers that build all of the responses ---

import boto3
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


import random


def get_recommendation(user, address):

    try :
        LIST_LIMIT = 5

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Hospital1')

        #user = "as5446" #Put user emailid here

        uid = str(uuid.uuid4())  # Generating a random user id which will be the primary key
        hospital_list = []

        hospital_suggestion = dict()
        hospital_prediction = []  # Final List to be displayed to the user
        clinic_type = 'hospital'
        #address="10027"
        googleurl = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=AIzaSyBc2X0NVymIdHyO8k9XNDhUBclPq6NemK4"

        with urlopen(googleurl) as r:
            data = json.loads(r.read())
        latlong = data["results"][0]["geometry"]["location"]
        latitude = latlong["lat"]
        longitude = latlong["lng"]

        clinicsURL = "https://api.foursquare.com/v2/venues/search?ll=" + str(latitude) + "," + str(
            longitude) + "&radius=15000&query=" + clinic_type + "&client_id=1TCDH3ZYXC3NYNCRVL1RL4WEGDP4CHZSLPMKGCBIHAYYVJWA&client_secret=VASKTPATQLSPXIFJZQ0EZ4GDH2QAZU1QGEEZ4YDCKYA11V2J&v=20160917"
        with urlopen(clinicsURL) as r:
            data = json.loads(r.read())

        venues = data["response"]["venues"]
        for val in venues:
            hospital_list.append(val["name"])

        #return hospital_list
        if len(hospital_list) == 0 or hospital_list is None:
            return hospital_prediction
        if len(hospital_list) < 5:
            LIST_LIMIT = len(hospital_list)

        #print ("len = ", len(hospital_list))

        for index, i in enumerate(hospital_list):
            hosp = i
            if (index== 10):
                break
            response = table.scan(
                FilterExpression=Attr('UserId').eq(user) & Attr('HospitalId').eq(hosp)
            )
            #print("NAMRATA",response, " == ", len(hospital_list), "i = ", index)
            req_data = response['Items']
            if len(req_data) == 0:
                #print ("ANUPAMA")
                pass
            else:
                temp = req_data[0]
                hosp_name = temp['HospitalId']
                hosp_count = temp['counts']
                hospital_suggestion[hosp_name] = int(hosp_count)

        # print("Hospital Dictionary",hospital_suggestion)


        #return hospital_list

        cnt = 0
        if len(hospital_suggestion) == 0:
            for j in hospital_list:
                hospital_prediction.append(j)
                cnt += 1
                if cnt == LIST_LIMIT:
                    break
        elif len(hospital_suggestion) < LIST_LIMIT:
            cnt = len(hospital_suggestion)
            for h in hospital_suggestion:
                hospital_prediction.append(h)
            for j in hospital_list:
                if j in hospital_suggestion:
                    pass
                else:
                    hospital_prediction.append(j)
                    cnt += 1
                    if cnt == LIST_LIMIT:
                        break
        elif len(hospital_suggestion) == LIST_LIMIT:
            suggestion1 = sorted(hospital_suggestion, key=hospital_suggestion.get)
            suggestion1 = suggestion1[::-1]
            for h in suggestion1:
                hospital_prediction.append(h)
        elif len(hospital_suggestion) > LIST_LIMIT:
            suggestion1 = sorted(hospital_suggestion, key=hospital_suggestion.get)
            suggestion1 = suggestion1[::-1]
            for h in suggestion1:
                hospital_prediction.append(h)
                cnt += 1
                if cnt == LIST_LIMIT:
                    break

        return hospital_prediction

        # print("Hospital Prediction recommendation",hospital_prediction)

        # NOW FROM HERE IT IS ADDING OR UPDATING DATABASE BASED ON USER SELECTION
    except :
        print(traceback.print_exc())


def record_user_choice(hospital_name, user):
    # user_choice = 3
    # hospital_name = hospital_prediction[user_choice-1]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Hospital1')
    uid = str(uuid.uuid4())

    response1 = table.scan(
        FilterExpression=Attr('UserId').eq(user) & Attr('HospitalId').eq(hospital_name)
    )
    req_data1 = response1['Items']
    if len(req_data1) == 0:
        response2 = table.put_item(Item={'ID': uid, 'UserId': user, 'HospitalId': hospital_name, 'counts': 1})
    else:
        temp1 = req_data1[0]
        primary = temp1['ID']
        counter = temp1['counts']
        counter += 1
        table.update_item(
            Key={'ID': primary},
            UpdateExpression="SET counts = :updated",
            ExpressionAttributeValues={':updated': counter}
        )

def text2int(textnum, numwords={}):

    if len(textnum) == 0 :
        return None
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          #raise Exception("Illegal word: " + word)
          return None

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end):

    return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', random.random())
    #print randomDate("5/8/2018 10:30 PM", "5/12/2018 4:50 AM", random.random())

def book_doctor(loc, user):

    hospital_list = []
    print ("here")
    print ("user = ", user, "loc = ", loc)
    hospital_list = get_recommendation(user, loc)
    print ("lissst WOHOOO= ",hospital_list)
    hospitals = ""
    hospital_details = []

    start_date = "5/9/2018 08:00 AM"
    end_date = "5/9/2018 11:00 PM"
    for index, h in enumerate(hospital_list) :
        rand_time = str(randomDate(start_date, end_date))
        details = {}
        details['name'] = h
        details['time'] = rand_time
        hospital_details.append(details)
        hospitals += str(index+1) + ". " + h + " At " + rand_time + "\n"

    return hospitals, len(hospital_list), json.dumps(hospital_details)


def send_mail(email_to, subject, attach_filename='Report.txt', email_body = 'Body'):
    ses = boto3.client('ses')

    email_from = 'nd2561@columbia.edu'
    #email_to = 'ag3900@columbia.edu'
    # email_cc = 'Email'

    msg = MIMEMultipart()
    msg['Subject'] = 'Report from HealthChat'
    msg['From'] = email_from
    msg['To'] = email_to

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'Multipart message.\n'

    # the message body
    part = MIMEText(subject)
    msg.attach(part)

    #filename = "Re.txt"
    filename = '/tmp/Output.txt'
    text_file = open(filename, "w")
    text_file.write(email_body)
    text_file.close()

    # the attachment
    part = MIMEApplication(open(filename, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=attach_filename)
    msg.attach(part)

    to_emails = [email_to, email_to]

    try:
        response = ses.send_raw_email(
            Source=email_from,
            Destinations=to_emails,
            RawMessage={
                'Data': msg.as_string(),
            }
        )
    except Exception as e:
        print(e)

def send_appointment(email_to, subject, email_body = 'Body'):
    ses = boto3.client('ses')

    email_from = 'nd2561@columbia.edu'
    #email_to = 'ag3900@columbia.edu'
    # email_cc = 'Email'

    try :
        response = ses.send_email(
            Source = email_from,
            Destination={
                'ToAddresses': [
                    email_to,
                ],

            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': email_body
                    }
                }
            }
        )
    except Exception as e:
        print(e)


def build_response_card(items, question_type):
    buttons = []
    title = None
    sub_title = None
    disease_id = None

    for item in items:

        if question_type == "single":
            button_dict = {}
            title = item['name']
            disease_id = item['id']
            button_dict['text'] = "Yes"
            button_dict['value'] =  "present"

            buttons.append(button_dict)
            button_dict = {}
            button_dict['text'] = "No"
            button_dict['value'] = "absent"

            buttons.append(button_dict)
            button_dict = {}
            button_dict['text'] = "Dont Know"
            button_dict['value'] = "unknown"

            buttons.append(button_dict)
        else:
            button_dict = {}
            button_dict['text'] = item['name']
            button_dict['value'] = item['id']
            buttons.append(button_dict)

    response_card = {
        "version": 1,
        "contentType": "application/vnd.amazonaws.card.generic",
        "genericAttachments": [
            {
                "title": title,
                "subTitle": sub_title,
                "buttons": buttons
            }
        ]
    }

    return response_card, disease_id


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card=None):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message,
            'responseCard': response_card

        }
    }


def close(session_attributes, fulfillment_state, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def isvalid_age(age):
    # at the beginning
    LOWER_LIMIT_AGE = 0
    UPPER_LIMIT_AGE = 200
    return (int(age) > LOWER_LIMIT_AGE and int(age) < UPPER_LIMIT_AGE)


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_profile(slots):
    age = try_ex(lambda: slots['Age'])
    #gender = try_ex(lambda: slots['Gender'])

    if age and not isvalid_age(age):
        return build_validation_result(
            False,
            'Age',
            'You have entered an invalid age.  Can you try to input again?'.format(age)
        )

    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """


def generate_disease(age, gender):
    return "I think you are suffering from cold"


def process_response(text, age, gender, evidence_list, disease_id, initial=False):
    api = infermedica_api.get_api()
    question_text = None
    response_2 = None
    response_card = None
    conditions = None
    attr = "disable_groups"

    print ("here")

    request = infermedica_api.Diagnosis(sex=gender.lower(), age=int(age))

    if evidence_list is None or (not evidence_list) or evidence_list == "[]":
        evidence_list = []
        response = api.parse(text, include_tokens=True)
        try:
            for mention in response.mentions:
                m = mention.to_dict()
                request.add_symptom(m['id'], m['choice_id'], initial=initial)
                d = {}
                d['id'] = m['id']
                d['choice_id'] = m['choice_id']
                d['initial'] = initial
                evidence_list.append(d)

            request.set_extras(attr, True)
            response_2 = api.diagnosis(request)

            #print("resp 2 =", response_2)
        except:
            print(traceback.print_exc())
    else:
        evidence_list = json.loads(evidence_list)
        initial = False

        #print("here list = ", evidence_list)

        for evidence in evidence_list:
            #print("evidence = ", evidence)
            if 'initial' in evidence:
                initial = evidence['initial']
            request.add_symptom(evidence['id'], evidence['choice_id'], initial=initial)

        try:
            #print("adding")
            #fields = text.split()
            if text != "go back" :
                list_words = text.split()
                #print ("fields = ", text)
                fields = []
                yes_inputs = ['yes', 'yep', 'ya', 'yeah', 'correct', 'right', 'hmm', 'present', 'yo', 'haa']
                no_inputs = ['no', 'nope', 'wrong', 'nah', 'absent', 'ni', 'na']

                for word in list_words :
                    if word in yes_inputs:
                        fields = [disease_id, "present"]
                        break
                    elif word in no_inputs:
                        fields = [disease_id, "absent"]
                        break

                if len(fields) == 0 :
                    fields = [disease_id, 'unknown']

                print("fields = ", fields)
                request.add_symptom(fields[0], fields[1], initial=initial)
                d = {}
                d['id'] = fields[0]
                d['choice_id'] = fields[1]
                evidence_list.append(d)

            request.set_extras(attr, True)
            response_2 = api.diagnosis(request)

            print("res2 = ", response_2)
        except:
            print(traceback.print_exc())

    if response_2.question:
        question_text = response_2.question.text
        question_type = response_2.question.type

        try:
            items = response_2.question.items
            if items:
                response_card, disease_id = build_response_card(items, question_type)
        except:
            print(traceback.print_exc())

    if response_2.conditions:
        conditions = response_2.conditions

    print("question = ", question_text)
    print("card = ", response_card)

    return question_text, response_card, json.dumps(evidence_list), json.dumps(conditions), disease_id


def infer_disease(intent_request):
    response = None
    response_card = None
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    current_slot = try_ex(lambda: session_attributes['current_slot'])

    gender = try_ex(lambda: intent_request['sessionAttributes']['Gender'])
    age = try_ex(lambda: intent_request['sessionAttributes']['Age'])
    symptom = try_ex(lambda: intent_request['currentIntent']['slots']['Symptom'])
    input = try_ex(lambda: intent_request['inputTranscript'])
    evidence_list = try_ex(lambda: intent_request['sessionAttributes']['evidenceList'])
    disease_id = try_ex(lambda: intent_request['sessionAttributes']['currentDisease'])


    conditions = try_ex(lambda: intent_request['sessionAttributes']['conditions'])

    if input is not None :
        input = input.lower()

    # Implement ask again
    if input == "go back" and evidence_list is not None :
        try :
            e = json.loads(evidence_list)
            e.pop()
            evidence_list = json.dumps(e)
        except :
            print(traceback.print_exc())

    if current_slot == "age" :
        # validate age here

        #age_flag = False
        valid_age = None
        if RepresentsInt(input)  : #and ( int(input) < 0 or int(input) > 200))  : # check for string input invalid case

            if  ( int(input) < 0 or int(input) > 200)  :
                valid_age = None

            else :
                #age_flag = True
                valid_age = int(input)

        else :
            # To handle multiple words in a sentence
            valid_age = text2int(input)

            if valid_age is None :
                list_words = input.split()
                for index, word in enumerate(list_words) :
                    valid_age = text2int(word)

                    if valid_age is not None :
                        break
                    if index < len(list_words) - 1 : # eg fifty five
                        valid_age = text2int(list_words[index] + " " + list_words[index+1])

                    if valid_age is not None :
                        break





        if valid_age is not None :
            session_attributes['current_slot'] = "gender"
            age = str(valid_age)
            session_attributes['Age'] = valid_age

        else :
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Symptom',
                {
                    'contentType': 'PlainText',
                    'content': 'Please enter a valid age'
                },
                response_card
            )


    if not age :
        session_attributes['current_slot'] = "age"
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            intent_request['currentIntent']['slots'],
            'Symptom',
            {
                'contentType': 'PlainText',
                'content': 'Whats your age?'
            },
            response_card
        )

    if current_slot == "gender":
        # validate age here

        male_list = ["male", "males", "boy", "boys", "man", "men", "mens", "mans", "kid", "guy"]
        female_list = ["female", "females", "gal", "girl", "girls", "woman", "women", "womens", "womans", "girly"]
        gender = None

        list_words = input.split()

        for word in list_words : # To handle gender contained in any sentence form
            if word in male_list :
                gender = "male"
                break
            elif word in female_list:
                gender = "female"
                break

        if gender is None :
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Symptom',
                {
                    'contentType': 'PlainText',
                    'content': 'Please enter a valid gender'
                },
                response_card
            )

        else :
            session_attributes['Gender'] = gender
            session_attributes['current_slot'] = "disease"
            content = 'Could you tell me more about your health issue ?'

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Symptom',
                {
                    'contentType': 'PlainText',
                    'content': content
                },
                response_card
            )

    if not gender:
        session_attributes['current_slot'] = "gender"
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            intent_request['currentIntent']['slots'],
            'Symptom',
            {
                'contentType': 'PlainText',
                'content': 'Whats your gender?'
            },
            response_card
        )


    if input and age and gender:


        try:
            response, response_card, evidence_list, conditions, disease_id = process_response(input, age, gender, evidence_list, disease_id, True)
            session_attributes['conditions'] = conditions
        except:
            print(traceback.print_exc())
    print(response, end="\n\n")

    # Load confirmation history and track the current reservation.
    profile = json.dumps({
        'Age': age,
        'Gender': gender,
    })

    session_attributes['currentProfile'] = profile
    session_attributes['currentResponse'] = response
    session_attributes['currentInput'] = input
    session_attributes['evidenceList'] = evidence_list
    session_attributes['currentDisease'] = disease_id


    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value

        if not age:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Age',
                {
                    'contentType': 'PlainText',
                    'content': 'Whats your age?'
                },
                response_card
            )

        if not gender:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Gender',
                {
                    'contentType': 'PlainText',
                    'content': 'Whats your gender?'
                },
                response_card
            )



        if not symptom:
            content = 'Could you tell me more about your health issue ?'
            if response is not None:
                content = response
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Symptom',
                {
                    'contentType': 'PlainText',
                    'content': content
                },
                response_card
            )



        # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  Pass price
        # back in sessionAttributes once it can be calculated; otherwise clear any setting from sessionAttributes.

        session_attributes['currentProfile'] = profile
        session_attributes['currentResponse'] = response
        session_attributes['currentInput'] = input
        return delegate(session_attributes, intent_request['currentIntent']['slots'])


    #session_attributes['InferredDisease'] = 'disease'
    session_attributes['currentResponse'] = response
    session_attributes['currentInput'] = input


    answer = "Thanks ! Would you like to book doctor's appointment ?"
    conditions_list = []
    try :

        conditions = json.loads(conditions)
        condition_name = conditions[0]['name']
        #condition_prob = str(conditions[0]['probability'])

        if ( len(conditions) < 5 ):
            conditions_list = conditions[:len(conditions)]
        else :
            conditions_list = conditions[:5]

        answer = "You are likely suffering from " + condition_name + " " + ". Please enter 'book doctor' for appointment or 'get report' for report."
        #+ " with " + condition_prob + " probability. " + answer
        session_attributes['conditionsList'] = json.dumps(conditions_list)
        session_attributes['diagnosis'] = "True"
    except Exception as e:
        print(e)

    session_attributes['conditionsList'] = json.dumps(conditions_list)

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
             # 'content': 'Thanks, Let me see how i can help '
            'content': answer

        }
    )

def get_doctor(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    loc = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    hospital_choice = try_ex(lambda: intent_request['currentIntent']['slots']['HospitalChoice'])
    #hospitals = try_ex(lambda: session_attributes['hospitals'])
    num_hospitals = try_ex(lambda: session_attributes['numHospitals'])
    recipient_email = try_ex(lambda: intent_request['currentIntent']['slots']['Email'])
    session_email = try_ex(lambda: session_attributes['email'])

    response_card = None
    content = "Doctor's Appointment Booked"
    print("Intent req", intent_request)

    if session_email is None:
        session_attributes['email'] = recipient_email
    else:
        recipient_email = session_email

    if hospital_choice is not None:
        #hospital_choice = int(hospital_choice)
        if hospital_choice == "0":
            content = "Thanks. Happy to help anytime !"
            return close(
                session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': content

                }
            )
        elif "." in hospital_choice or int(hospital_choice) < 0 or (num_hospitals is not None and int(hospital_choice) > int(num_hospitals)):
            print ("num hos = ", num_hospitals)
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'HospitalChoice',
                {
                    'contentType': 'PlainText',
                    'content': 'Please enter a valid hospital choice .'
                },
                response_card
            )



    if intent_request['invocationSource'] == 'DialogCodeHook':
        print(intent_request['currentIntent']['slots'])
        if not loc:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Location',
                {
                    'contentType': 'PlainText',
                    'content': 'Please enter your location zipcode'
                },
                response_card
            )

        if recipient_email is None and session_email is None:
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'Email',
                {
                    'contentType': 'PlainText',
                    'content': 'Please enter your email id.'
                },
                response_card
            )

        if not hospital_choice:

            hospitals, num_hospitals, hospital_details = book_doctor(loc, recipient_email)

            if num_hospitals == 0 :
                content = "Sorry. I could not find a hospital nearby. Please try 'book doctor' again with a different pincode."
            else :
                content = 'Here are the recommended nearby hospitals.'+ hospitals + ' \n Please enter the hospital number where you want to book appointment. Enter 0 to skip.'

            session_attributes['hospitals'] = json.dumps(hospitals)
            session_attributes['numHospitals'] = num_hospitals
            session_attributes['hospitalDetails'] = hospital_details





            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'HospitalChoice',
                {
                    'contentType': 'PlainText',
                    'content': content
                },
                response_card
            )

        #print("LOCATION", loc)

        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    hospital_list = json.loads(session_attributes['hospitalDetails'])
    session_attributes['hospitalName'] = hospital_list[int(hospital_choice)-1]['name']
    session_attributes['hospitalTime'] = hospital_list[int(hospital_choice)-1]['time']

    record_user_choice(session_attributes['hospitalName'], recipient_email)

    email_body = get_appointment_body(session_attributes['hospitalName'], session_attributes['hospitalTime'])

    subject = 'Appointment Details from HealthChat'



    send_appointment(recipient_email, subject, email_body)

    print ("recipient email = ", recipient_email)
    content = content + ". Appointment details sent to " + recipient_email
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': content

        }
    )

def get_email_body(profile, conditions_list):

    body = ""

    try :
        profile = json.loads(profile)
        body += "Age: " + profile['Age'] + "\n"
        body += "Gender: " + profile['Gender'] + "\n\n"

        conditions_list = json.loads(conditions_list)
        for c in conditions_list:
            body += "Disease: " + c['name'] + "  Probability: " + str(c['probability']) + "\n\n"
    except :
        print(traceback.print_exc())

    return body


def get_appointment_body(hospital_name, hospital_time):

    body = ""

    try :
        id = str(random.randint(1, 10000))
        body += "Your appointment has been booked at : " + hospital_name  +  "\n"  + \
                 "Time : " + hospital_time + " \n\nAppointment ID - " + id


    except :
        print(traceback.print_exc())

    return body

def get_confirmation(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    name = try_ex(lambda: session_attributes['hospitalName'])

    if name is None :
        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': "Please enter 'book appointment' to book appointment first !"

            }
        )


    recipient_email = try_ex(lambda: intent_request['currentIntent']['slots']['Email'])

    if not recipient_email:
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            intent_request['currentIntent']['slots'],
            'Email',
            {
                'contentType': 'PlainText',
                'content': 'Please enter your email address.'
            },
        )

    time = try_ex(lambda: session_attributes['hospitalTime'])
    email_body = get_appointment_body(name, time)
    subject = 'Appointment Details from HealthChat'
    filename = 'Appointment Details.txt'
    #send_mail(recipient_email, subject, filename, email_body)
    send_appointment(recipient_email, subject, email_body)
    session_attributes['email'] = recipient_email

    content =  "Appointment details send to  " + recipient_email + "!"
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': content
        }
    )






def get_report(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    recipient_email = try_ex(lambda: intent_request['currentIntent']['slots']['Email'])
    session_email = try_ex(lambda: session_attributes['email'])
    diagnosis = try_ex(lambda: session_attributes['diagnosis'])
    conditions_list = try_ex(lambda: session_attributes['conditionsList'])
    currentDisease = try_ex(lambda: session_attributes['currentDisease'])
    profile = None

    sess = ""
    for key in session_attributes :
        sess += key

    print ("session  = ", session_attributes)
    if conditions_list is None :
        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': "Please enter 'I am not feeling well' to begin the diagnosis !"

            }
        )

    if not recipient_email and not session_email:
        return elicit_slot(
            session_attributes,
            intent_request['currentIntent']['name'],
            intent_request['currentIntent']['slots'],
            'Email',
            {
                'contentType': 'PlainText',
                'content': 'Please enter your email address.'
            },
        )

    profile = try_ex(lambda: session_attributes['currentProfile'])

    email_body = get_email_body(profile, conditions_list)
    subject = 'Report from HealthChat'
    filename = 'Report.txt'

    if recipient_email is None :
        recipient_email = session_email

    send_mail(recipient_email, subject, filename, email_body)
    session_attributes['email'] = recipient_email
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': "Your Report has been sent to " + recipient_email + "!"

        }
    )

# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies   an intent for this bot.
    """

    logger.debug(
        'dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'InferDisease':
        return infer_disease(intent_request)
    elif intent_name == 'GetReport':
        return get_report(intent_request)
    elif intent_name == 'GetDoctor':
        return get_doctor(intent_request)
    elif intent_name == 'GetConfirmation':
        return get_confirmation(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    # logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
