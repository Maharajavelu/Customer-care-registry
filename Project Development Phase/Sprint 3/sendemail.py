import smtplib
from random import *
from email.message import EmailMessage
otp = randint(000000,999999)

def usermail(TEXT,tomail):
    msg = EmailMessage()
    msg['Subject'] = 'Complaint Registered | Customer Care Registry'
    msg['From'] = 'customercare.in2022@gmail.com'
    msg['To'] = tomail
    msg.set_content('')
    msg.add_alternative(TEXT,subtype='html')


    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('customercare.in2022@gmail.com','gihwtunyaukhvwmx')
        smtp.send_message(msg)
        

def agentmail(TEXT,tomail):
    msg = EmailMessage()
    msg['Subject'] = 'New Complaint Registered | Customer Care Registry'
    msg['From'] = 'customercare.in2022@gmail.com'
    msg['To'] = tomail
    msg.set_content('')
    msg.add_alternative(TEXT,subtype='html')


    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('customercare.in2022@gmail.com','gihwtunyaukhvwmx')
        smtp.send_message(msg)

def verify(MES, tomail):
    msg = EmailMessage()
    msg['Subject'] = 'New Complaint Registered | Customer Care Registry'
    msg['From'] = 'customercare.in2022@gmail.com'
    msg['To'] = tomail
    msg.set_content('')
    msg.add_alternative(MES,subtype='html')

    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('customercare.in2022@gmail.com','gihwtunyaukhvwmx')
        smtp.send_message(msg)