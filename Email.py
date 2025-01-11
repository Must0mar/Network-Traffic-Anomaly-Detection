import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import smtplib
import time
import re
from dotenv import load_dotenv
import os
load_dotenv()

network_file_path = "network_traffic_summary.json"
email_file_path = "emails.json"
CLAUDE_API_KEY =  os.getenv('API_KEY')
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)

last_timestamp = None

with open(network_file_path, "r") as file:
    data = json.load(file)
with open(email_file_path, "r") as file:
    email = json.load(file)

emails = email['emails']
total_anomalies = data["total_anomalies"]
anomalies_by_type = data["anomalies_by_type"]

anomalies_timestamped = {}

if anomalies_by_type:
    for key in anomalies_by_type.keys():
        anomalies_timestamped[key] = None


def analyze_with_claude(prompt):
    print("Sending Request")
    try:
        response = anthropic_client.completions.create(
            model="claude-2",  
            max_tokens_to_sample=8192,
            temperature=0.8,
            prompt=f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}"
        )
        return response.completion
    except Exception as e:
        print(e)
    return None

def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

sender_email = "nads.capstone.2024@gmail.com"
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_password = "uems ifhn ksca monz"

def getResponse(attack_type):
    prompt= (
        f"""
        Generate an email to notify a non-technical user about a detected network anomaly of type '{attack_type}'. Provide the response solely as a JSON object containing the body of the email in three languages(do not include anything similar to this: "Here is the JSON object with the email body in 3 languages:"): English (en), Kurdish Sorani (ku), and Arabic (ar). The JSON object should have the following structure:

        {{
            "en": "This is the email body in English.",
            "ku": "ئەمە ڕێنماییەکانە بۆ کوردی.",
            "ar": "هذه تعليمات باللغة العربية."
        }}

        The content for each language should include:

        1. A clear summary of the anomaly, with a simple explanation of what '{attack_type}' means.
        2. A brief, non-technical explanation of the possible cause of the anomaly.
        3. Step-by-step instructions for the user to verify or address the issue, easy to understand for a non-technical user.
        4. A friendly, neutral tone, avoiding unnecessary alarm, while keeping the content concise and user-friendly.

        Note: do not include any message of contacting us, include instructions like how to reset the router setting or credentials that will benefit to increase the security of our network, the instruction must be easy enough to be done by a non-techincal person.

        Ensure that the response consists only of the JSON object with no additional text, formatting, or commentary.
                    """
    )
    return analyze_with_claude(prompt)
def send_all_mails(emails, alert):
    for email in emails:
        send_email(sender_email, email, "Network Attack Alert", alert , smtp_server, smtp_port, sender_password)
        print(timeTest, email)

    

def create_email_body(json_str):
    match = re.search(r'\{.*\}', json_str, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in the input string.")
    
    json_content = match.group(0).strip()

    data = json.loads(json_content)

    email_body = (
        "Instructions in English:\n"
        f"{data['en']}\n\n"
        "ڕێنماییەکان بە زمانی کوردی:\n"
        f"{data['ku']}\n\n"
        "تعليمات باللغة العربية:\n"
        f"{data['ar']}"
    )

    return email_body
def extract_and_save_json(text, output_filename):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in the input text.")
    
    json_content = match.group(0).strip()

    data = json.loads(json_content)

    formatted_data = {
        "en": data["en"],
        "ku": data["ku"],
        "ar": data["ar"]
    }

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)

print()
while True:
    
    current_time = datetime.now()   
    count = 0
    if total_anomalies > 0:
        timeTest = datetime.now()
        extract_and_save_json
        for key in anomalies_timestamped:
            if key == 1:
                attack_type = "Port Scanning"
            elif key == 2:
                attack_type = "DOS attack"
            else:
                attack_type = "network attacks"
            
            if anomalies_timestamped[key] is None:
                print(timeTest, key, email)
                response = getResponse(attack_type)
                send_all_mails(emails, create_email_body(response))  
                extract_and_save_json(response, "alert.json")
                anomalies_timestamped[key] = current_time
                print(count)
                continue  

            if anomalies_timestamped[key] is None or (current_time - anomalies_timestamped[key] > timedelta(minutes=1)):
                print(timeTest, key, email)
                print(count)
                
                response = getResponse(attack_type)
                extract_and_save_json(response, "alert.json")
                send_all_mails(emails, create_email_body(response))                

                anomalies_timestamped[key] = current_time  