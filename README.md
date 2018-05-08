## HealthChatProject
Cloud Computing and Big Data (COMS 6998) project

## Description
This project implements a Chatbot (text and voice) Web application with the following functionalities:
1. Disease diagnosis via question answering through response cards
2. Report generation based on Step 1. 
3. Hospital recommendation (based on user preference history)
4. Booking the doctor's appointment based on user selection in Step 3.

## Team ID: 11
1. Anupama Gupta(ag3900)
2. Namrata Uday Devadiga(nd2561)

# AWS Services Involved
Lex, Lambda, DynamoDB, Cognito, SES, S3

## Intents
1. InferDisease  <br />
   Example Utterances : <br />
   a. I am not feeling well <br />
   b. I am not ok <br />
   c. I am not good <br /> 
   d. I am sick <br /> <br />
   
  Fulfilment : <br />
   a. tell me <br /> 
   b. stop asking <br />
   c. whats my disease <br />
   
2. BookDoctor <br />
   Example Utterances : <br /> 
   a. book doctor <br />
   b. get doctor <br /> 
   c. book doctor's appointment <br /> 
  
3. GetReport <br />
   Example Utterances : <br />
   a. get my report  <br />
   b. i want report  <br />
   c. send me details  <br />

## Example Conversation 
User - I am not feeling well. <br />
Bot - Whats your age ? <br />
User - 16 <br />
Bot - Whats your gender ? <br />
User - Female <br />
Bot - Could you tell me more about your health issue ? <br />
User - I have fever <br />
Bot - Do you have a body temperature of 101 °F (38 °C) or higher? <br />
User - Yes <br />
Bot - Have you had contact with someone with chickenpox in the last 3 weeks? <br />
User - Yes <br />
User - tell me <br />
Bot - You are likely suffering from Chickenpox . Please enter 'book doctor' for appointment or 'get report' for report. <br />
User - get report <br />
Bot - Please enter your email address. <br />
User - ag3900@columbia.edu <br />
Bot - Your Report has been sent to ag3900@columbia.edu! <br />
User - book doctor <br />
Bot - Please enter your location zipcode <br />
User - 10027 <br />
Bot - Here are the recommended nearby hospitals.1. The Mount Sinai Hospital - New York City At 05/09/2018 01:35 PM 2. New York Presbyterian Hospital Weill Cornell Medical Center At 05/09/2018 04:49 PM 3. Milstein Hospital Building At 05/09/2018 10:19 AM 4. Riverside Animal Hospital North At 05/09/2018 08:14 AM 5. Hospital for Special Surgery At 05/09/2018 01:08 PM Please enter the hospital number where you want to book appointment. Enter 0 to skip. <br />
User - 1 <br />
Bot - Doctor's Appointment Booked. Appointment details sent to ag3900@columbia.edu <br />

## Example Conversation 2 (Enter "Go back" to re-answer the last question) 
User - I am not feeling well. <br />
Bot - Whats your age ? <br />
User - 16 <br />
Bot - Whats your gender ? <br />
User - Female <br />
Bot - Could you tell me more about your health issue ? <br />
User - I have fever <br />
Bot - Do you have a body temperature of 101 °F (38 °C) or higher? <br />
User - Yes <br />
Bot - Have you had contact with someone with chickenpox in the last 3 weeks? <br />
User - go back <br />
Bot - Do you have a body temperature of 101 °F (38 °C) or higher? <br />
User - No <br />
Bot - Have you noticed a partial or total loss of your sense of smell? <br />
User - Yes <br />
User - tell me <br />
Bot - You are likely suffering from Acute rhinosinusitis . Please enter 'book doctor' for appointment or 'get report' for report. <br />

