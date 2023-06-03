"""
The code below is built to email multiple recipients at once with the concept of automation
"""
import schedule
import time
import smtplib
import ssl
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import socket
import json
import random


# function that receives the data of sent email and saves it on the json file
def save_email_record(email_data):
    while True:
        # load the json file for logging email history, if it does not exist create it
        try:
            with open("Email_History.json", "r") as file:
                email_history = json.load(file)
        except FileNotFoundError:
            email_history = {}
        except json.decoder.JSONDecodeError:
            email_history = {}
        # assigns each email a unique randomly generated id, to save it as a new record in the json file
        email_id = str((round(random.random() * 10000000000)))
        if "email" + email_id not in email_history:
            email_record = email_data
            email_history["email" + str(email_id)] = email_record
            with open("Email_History.json", "w") as file:
                json.dump(email_history, file)
            break


# this function will be called based on the scheduled time
# sends email messages with an attached file to several emails that are read from a text file.
def sending_emails():
    sender = 'testtest0000006@gmail.com'
    password = 'eqnmuzsgcqzaepmg'
    # The list of receivers is loaded from the Receivers_list.txt file
    receivers = open("Receivers_list.txt", "r").read().splitlines()
    try:
        # connect to email server (gmail in this case)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            for receiver in receivers:
                # compose the email
                text = 'Hello ' + receiver + ", here are your daily reports for today. "
                msg = MIMEMultipart(text)
                msg['Subject'] = 'Daily reports for ' + receiver
                msg['From'] = sender
                msg['To'] = receiver
                # attach the attachment to the email
                daily_report = 'DailyReport.txt'
                with open(daily_report, 'r') as f:
                    part = MIMEApplication(f.read(), Name=basename(daily_report))
                part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(daily_report))
                msg.attach(part)
                # send the email
                try:
                    server.sendmail(sender, receiver, msg.as_string())
                    print("Successfully sent email to " + receiver)
                    # crating the dictionary with the email data
                    email_record = {
                        "sender": sender,
                        "receiver": receiver,
                        "subject": msg['Subject'],
                        "text": text,
                        "attachment": daily_report
                    }
                    save_email_record(email_record)
                # if faced with an invalid email address, print a message to the console
                # and log the error in Email_History.json
                except smtplib.SMTPRecipientsRefused:
                    print("The recipient " + receiver + " is not a valid email address")
                    email_record = {
                        "errorMessage": receiver + " is not a valid email address"
                    }
                    save_email_record(email_record)
    # if the user's credentials are incorrect, print a message to the console and log the error in Email_History.json
    except smtplib.SMTPAuthenticationError:
        print("Could not login to your account. Please check if your email and password are correct...")
        email_record = {
            "errorMessage": "There was a problem while signing in to your email"
        }
        save_email_record(email_record)
    # if connection to server is unsuccessful, print a message to the console and log the error in Email_History.json
    except socket.gaierror:
        print("Could not connect to server...")
        email_record = {
            "errorMessage": "There was a problem while connecting to server"
        }
        save_email_record(email_record)


# setting a schedule to run the script
schedule.every().day.at("09:00").do(sending_emails)

while True:
    schedule.run_pending()
    time.sleep(1)
