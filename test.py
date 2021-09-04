import smtplib

import tinydb

import config
import main

rec = main.get_mail_recipients()

data = main.fetch_active_giveaways()

filtered = main.filter_giveaways(data, False, 10)

msg = main.build_email_message(filtered, rec)

def send_email():
    client = smtplib.SMTP_SSL('example.com', local_hostname='example.com')
    client.login(config.smtp_username, config.smtp_password)
    print(msg)
    client.sendmail(config.smtp_username, rec, msg)

def db_data():
    db = tinydb.TinyDB(config.db_file)
    print(db)
    table = db.table("games")
    print(table)
