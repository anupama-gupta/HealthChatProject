
import json
import datetime
import time
import os
import dateutil.parser
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


import config

config.setup_examples()
import infermedica_api

import traceback
# --- Helpers that build all of the responses ---



def build_response_card(items, question_type):

    buttons = []
    title = None
    sub_title = None

    for item in items :

        if question_type == "single":
            button_dict = {}
            title = item['name']
            button_dict['text'] = "Yes"
            button_dict['value'] = item['id'] + " " + "present"

            buttons.append(button_dict)
            button_dict = {}
            button_dict['text'] = "No"
            button_dict['value'] = item['id'] + " " + "absent"

            buttons.append(button_dict)
            button_dict = {}
            button_dict['text'] = "Dont Know"
            button_dict['value'] = item['id'] + " " + "unknown"

            buttons.append(button_dict)
        else :
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

    return response_card


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
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


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
    return ( int(age) > LOWER_LIMIT_AGE and int(age) < UPPER_LIMIT_AGE )


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }



def validate_profile(slots):
    age = try_ex(lambda: slots['Age'])
    gender = try_ex(lambda: slots['Gender'])

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

def process_response(text, age, gender, evidence_list, initial=False):

    api = infermedica_api.get_api()
    question_text = None
    response_2 = None
    response_card = None
    conditions = None

    #request = infermedica_api.Diagnosis(sex=gender.lower(), age=int(age))  # Behaves unsual
    request = infermedica_api.Diagnosis(sex="male", age=20)

    if evidence_list is None or (not evidence_list) or evidence_list == "[]" :
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

            response_2 = api.diagnosis(request)

            print ("resp 2 =" , response_2)
        except:
            print(traceback.print_exc())
    else :
        evidence_list = json.loads(evidence_list)
        initial = False

        print ("here list = ", evidence_list)

        for evidence in evidence_list :
            print ("evidence = ", evidence)
            if 'initial' in evidence :
                initial = evidence['initial']
            request.add_symptom(evidence['id'], evidence['choice_id'], initial=initial)

        try :
            print ("adding")
            fields = text.split()
            if len(fields) == 1 :
                fields.append("present")

            request.add_symptom(fields[0], fields[1], initial=initial)
            d = {}
            d['id'] = fields[0]
            d['choice_id'] = fields[1]
            response_2 = api.diagnosis(request)
            evidence_list.append(d)
            print ("res2 = ", response_2)
        except :
            print(traceback.print_exc())

    if response_2.question :
        question_text = response_2.question.text
        question_type = response_2.question.type

        try :
            items = response_2.question.items
            if items:
               response_card = build_response_card(items, question_type)
        except :
            print (traceback.print_exc())

    if response_2.conditions :
        conditions = response_2.conditions

    print ("question = ", question_text)
    print ("card = ", response_card)
    return question_text, response_card, json.dumps(evidence_list), json.dumps(conditions)



def infer_disease(intent_request):

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    age = try_ex(lambda: intent_request['currentIntent']['slots']['Age'])
    gender = try_ex(lambda: intent_request['currentIntent']['slots']['Gender'])
    symptom = try_ex(lambda: intent_request['currentIntent']['slots']['Symptom'])
    input = try_ex(lambda: intent_request['inputTranscript'])
    evidence_list = try_ex(lambda: intent_request['sessionAttributes']['evidenceList'])

    if not age :
        age = try_ex(lambda: intent_request['sessionAttributes']['Age'])
    if not gender :
        gender = try_ex(lambda: intent_request['sessionAttributes']['Gender'])

    age = "20"
    gender = "male"
    print ("input = ", input)
    response = None
    response_card = None



    #if input and age and gender :
    if input :
        try :
            response, response_card, evidence_list, conditions = process_response(input, age, gender, evidence_list, True)
        except :
            pass
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
    session_attributes['conditions'] = conditions


    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value

        if not age :
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

        if not gender :
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

        if not symptom :
            content = 'Got it. Could you tell more about it ?'
            if response is not None :
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

        validation_result = validate_profile(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                response_card
            )

        # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  Pass price
        # back in sessionAttributes once it can be calculated; otherwise clear any setting from sessionAttributes.
        if age and gender :
            # The price of the hotel has yet to be confirmed.
            disease = generate_disease(age, gender)
            session_attributes['currentDisease'] = disease
        else:
            try_ex(lambda: session_attributes.pop('currentDisease'))


        session_attributes['currentProfile'] = profile
        session_attributes['currentResponse'] = response
        session_attributes['currentInput'] = input
        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    # Booking the hotel.  In a real application, this would likely involve a call to a backend service.
    #logger.debug('bookHotel under={}'.format(reservation))

    #try_ex(lambda: session_attributes.pop('currentReservationPrice'))
    #try_ex(lambda: session_attributes.pop('currentReservation'))
    session_attributes['InferredDisease'] = 'disease'
    session_attributes['currentResponse'] = response
    session_attributes['currentInput'] = input
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, Let me see how i can help '

        }
    )



# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies   an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'InferDisease':
        return infer_disease(intent_request)

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

    #logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
