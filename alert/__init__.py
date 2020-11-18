import json
import time
import tkinter
from tkinter import RIGHT, END

try:
    import tkinter
except ImportError:
    import Tkinter as tk

import requests
from boltiot import Bolt, Sms, Email

from alert import conf


def toggle_state(*_):
    if e1.var.get():
        button1['state'] = 'normal'
    else:
        button1['state'] = 'disabled'


def send_telegram_message(message):
    url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
    data = {"chat_id": conf.telegram_chat_id,
            "text": message
            }
    try:
        response = requests.request(
            "GET",
            url,
            params=data
        )
        print("This is the Telegram response")
        print(response.text)
        telegram_data = json.loads(response.text)
        return telegram_data["ok"]
    except Exception as e:
        print("An error occurred in sending the alert message via Telegram")
        print(e)
        return False


def get_bitcoin_price():
    URL = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,JPY,EUR,INR"  # REPLACE WITH CORRECT URL
    respons = requests.request("GET", URL)
    respons = json.loads(respons.text)
    current_price = respons["USD"]
    return current_price


mybolt = Bolt(conf.api_key, conf.device_id)
sms = Sms(conf.SSID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
mailer = Email(conf.MAILGUN_API_KEY, conf.SANDBOX_URL, conf.SENDER_MAIL, conf.RECIPIENT_MAIL)


def testVal(inStr, acttyp):
    if acttyp == '1':  # insert
        if not inStr.isdigit():
            return False
    return True


def printSomething():
    while True:
        textbox.update()
        c_price = get_bitcoin_price()
        textbox.update()
        _time = time.ctime()
        textbox.insert(END, "The Current Bitcoin Price is: " + str(get_bitcoin_price()) + " USD" + ", at " + str(
            time.ctime()) + ".\n")
        print(get_bitcoin_price(), str(time.ctime()))
        textbox.update()
        if c_price >= int(e1.get()):
            textbox.insert(END, "Alert!!!, The Current Bitcoin Price is: " + str(
                get_bitcoin_price()) + " USD" + ", at " + str(
                time.ctime()) + ".\n")
            # Enable Buzzer
            response_buzzer = mybolt.digitalWrite('0', 'HIGH')
            print(response_buzzer)
            buzzer_data = json.loads(response_buzzer)
            if buzzer_data["success"] == 1:
                textbox.insert(END, "Buzzer is now active.\n")
            else:
                textbox.insert(END, "Unable to activate buzzer due to " + str(buzzer_data["value"]) + ".\n")
            textbox.update()
            # Send SMS
            textbox.insert(END, "Sending an SMS.....\n")
            textbox.update()
            response_SMS = sms.send_sms(
                "Alert! The Bitcoin selling price is now : " + str(c_price) + " USD at " + str(_time) + ".")
            textbox.insert(END, "This is the response " + str(response_SMS) + ".\n")
            textbox.update()
            # Send Mail
            textbox.insert(END, "Making request to Mailgun to send an email.....\n")
            textbox.update()
            response_mail = mailer.send_email("PRICE ALERT", "Alert! The Bitcoin selling price is now : " + str(
                c_price) + " USD at " + str(_time))
            response_text = json.loads(response_mail.text)
            textbox.insert(END, "Response received from Mailgun is:" + str(response_text['message']) + ".\n")
            textbox.update()
            # Send Telegram Alert
            message = 'Alert! The Bitcoin selling price is now : ' + str(c_price) + ' USD at ' + str(_time)
            telegram_status = send_telegram_message(message)
            textbox.insert(END, "This is the Telegram status: " + str(telegram_status) + ".\n")
            textbox.update()
        else:
            response = mybolt.digitalWrite('0', 'LOW')
            textbox.insert(END, "Bitcoin price is still down, please try after sometime." + "\n")
            textbox.update()
        textbox.update()
        time.sleep(20)


master = tkinter.Tk()
master.title("-Bitcoin Price Alert and Prediction System-")
master.geometry('1440x900')
scrollbar = tkinter.Scrollbar(master)
scrollbar.pack(side=RIGHT, fill=tkinter.Y)
textbox = tkinter.Text(master)
textbox.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

# attach textbox to scrollbar
tkinter.Label(master, text="Enter the selling price of bitcoin in USD (only numerics)").place(relx=0.3, rely=0.1,
                                                                                              anchor=tkinter.CENTER)
e1 = tkinter.Entry(master, validate="key")
e1['validatecommand'] = (e1.register(testVal), '%P', '%d')
e1.var = tkinter.StringVar()
e1['textvariable'] = e1.var
e1.var.trace_add('write', toggle_state)
e1.place(relx=0.7, rely=0.1, anchor=tkinter.CENTER)

tkinter.Button(master,
               text='Quit',
               command=master.quit).place(relx=0.3, rely=0.9, anchor=tkinter.CENTER)
button1 = tkinter.Button(master,
                         text='Submit', command=printSomething, state='disabled')
button1.place(relx=0.7, rely=0.9, anchor=tkinter.CENTER)

textbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=textbox.yview)
tkinter.mainloop()
