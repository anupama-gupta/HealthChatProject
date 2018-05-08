# HealthChatProject
Cloud Computing and Big Data (COMS 6998) project

# Description
This project implements a Chatbot (text and voice) Web application with the following functionalities:
1. Disease diagnosis via question answering through response cards
2. Report generation based on Step 1. 
3. Hospital recommendation (based on user preference history)
4. Booking the doctor's appointment based on user selection in Step 3.

# Team ID: 11
1. Anupama Gupta(ag3900)
2. Namrata Uday Devadiga(nd2561)

# AWS Services Involved
Lex, Lambda, DynamoDB, Cognito, SES, S3

# Intents
1. InferDisease
   Example Utterances :
   a. I am not feeling well
   b. I am not ok
   c. I am not good
   d. I am sick
   
   Fulfilment :
   a. tell me
   b. stop asking
   c. whats my disease
   
2. BookDoctor
   Example Utterances :
   a. book doctor
   b. get doctor
   c. book doctor's appointment
  
3. GetReport
   Example Utterances :
   a. get my report
   b. i want report
   c. send me details

# Example Conversation
User - I am not feeling well.
Bot - Whats your age ?
User - 16
Bot - Whats your gender ?
User - Female
Bot - Could you tell me more about your health issue ?
User - I have fever
Bot - Do you have a body temperature of 101 °F (38 °C) or higher?
User - Yes
Bot - Have you had contact with someone with chickenpox in the last 3 weeks?
User - Yes
User - tell me
Bot - You are likely suffering from Chickenpox . Please enter 'book doctor' for appointment or 'get report' for report.
User - get report
Bot - Please enter your email address.
User - ag3900@columbia.edu
Bot - Your Report has been sent to ag3900@columbia.edu!
User - book doctor 
Bot - Please enter your location zipcode
User - 10027
Bot - Here are the recommended nearby hospitals.1. The Mount Sinai Hospital - New York City At 05/09/2018 01:35 PM 2. New York Presbyterian Hospital Weill Cornell Medical Center At 05/09/2018 04:49 PM 3. Milstein Hospital Building At 05/09/2018 10:19 AM 4. Riverside Animal Hospital North At 05/09/2018 08:14 AM 5. Hospital for Special Surgery At 05/09/2018 01:08 PM Please enter the hospital number where you want to book appointment. Enter 0 to skip.
User - 1
Bot - Doctor's Appointment Booked. Appointment details sent to ag3900@columbia.edu

# Example Conversation 2 (Enter "Go back" to re-answer the last question)
User - I am not feeling well.
Bot - Whats your age ?
User - 16
Bot - Whats your gender ?
User - Female
Bot - Could you tell me more about your health issue ?
User - I have fever
Bot - Do you have a body temperature of 101 °F (38 °C) or higher?
User - Yes
Bot - Have you had contact with someone with chickenpox in the last 3 weeks?
User - go back
Bot - Do you have a body temperature of 101 °F (38 °C) or higher?
User - No
Bot - Have you noticed a partial or total loss of your sense of smell?
User - Yes
User - tell me
Bot - You are likely suffering from Acute rhinosinusitis . Please enter 'book doctor' for appointment or 'get report' for report.

