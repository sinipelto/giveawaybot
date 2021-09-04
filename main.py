import smtplib
import uuid
from email import utils
from os import path

import requests
import tinydb

import config


def fetch_active_giveaways():
    url = config.base_url + "?" + config.param_type + "&" + config.param_sort
    
    print(f"GET {url}")
    
    resp = requests.get(url)
    
    if resp.status_code != 200:
        print(f"HTTP ERROR: Failed to make request: CODE: {resp.status_code} Content: {resp.content[:300]}...")
        raise requests.RequestException()
    
    print("HTTP 200 OK")
    
    return resp.json()


def init_db():
    try:
        tinydb.TinyDB(config.db_file).table(config.table_name).clear_cache()
    except:
        print(f"ERROR: Failed to init db: {sys.exc_info()}")
        raise


def giveaway_exists_db(id) -> bool:
    db = tinydb.TinyDB(config.db_file).table(config.table_name)
    if db.search(tinydb.where('id') == id):
        return True
    return False


def insert_giveaways(data):
    try:
        db = tinydb.TinyDB(config.db_file).table(config.table_name)
        for entry in data:
            if giveaway_exists_db(entry['id']):
                continue
            db.insert(entry)
    except:
        print(f"ERROR: Failed to insert new giveaways: {sys.exc_info()}")
        raise


def filter_giveaways(input, new_only: bool, min_value: float = None , max_value: float = None) -> list:
    filtered = []

    for entry in input:
        try:
            id = int(entry['id'])
            status = str(entry['status'])
            price = None

            if entry['worth'] == "N/A":
                continue
            else:
                price = float(entry['worth'][1:])

            if status != "Active":
                continue
            
            if min_value is not None and price < min_value:
                continue
            
            if max_value is not None and price > max_value:
                continue

            if new_only and giveaway_exists_db(id):
                continue
            
            filtered.append(entry)
            # print(entry)

        except:
            print(f"Failed entry: {entry}")
            print(f"Caught exception during filter: {sys.exc_info()}")

    print(f"Filtered count: {len(filtered)}")
    return filtered


def get_mail_recipients() -> list:
    if not path.exists(config.recipient_file):
        print("ERROR: Recipients file not found. Creating file..")
        f = open(config.recipient_file, "w+")
        f.close()
        return None

    recipients = []
    with open(config.recipient_file, "r") as f:
        for line in f.readlines():
            line = line.strip('\r').strip('\n').strip(" ")

            # If whitespace only or commented out, skip
            if line == "" or line[0] == "#":
                continue

            recipients.append(line)

    return recipients


def build_email_message(data, recipients) -> str:
    if type(recipients) is not list or len(recipients) <= 0:
        print("ERROR: Could not parse email recipients. Ensure recipients file is configured correctly.")
    
    message = ""
    
    sender = f"{config.sender_name} <{config.sender_email}>"
    subject = f"{config.email_title}"

    message += f"From: {sender}\r\n"
    message += f"To: " + ", ".join(recipients) + "\r\n"
    message += "MIME-Version: 1.0\r\n"
    message += "Content-Transfer-Encoding: 8bit\r\n"
    message += "Content-Type: text/html; charset=\"UTF-8\"\r\n"
    message += f"Date: {utils.localtime()}\r\n"
    message += f"Message-ID: {utils.make_msgid()}\r\n"
    message += f"Subject: {subject}\r\n"

    message += "New giveaways listed below:<br><br>\r\n"
    message += f"Current Configuration: Minimum Value: ${config.min_value}. Maximum Value: {config.max_value}.<br><br>\r\n"

    for entry in data:
        message += f"<img src='{entry['image']}' width='250' height='250'>"
        message += "<pre>    </pre>"
        message += f"<h1><a href='{entry['open_giveaway']}'>{entry['title']} (Value: {entry['worth']})</a></h1>"
        message += f"<p>Description: {entry['description']}</p>"
        message += f"<h3>Platform: {entry['platforms']}</h3>"
        message += "<br><br>"

    message += "<br><br>"
    message += "Sincerely,<br><br>"
    message += f"{config.sender_name}"
    
    return message.encode("utf-8")


def send_email(recipient_list, message):
    client = smtplib.SMTP_SSL(config.smtp_host, local_hostname=config.smtp_host)
    client.login(config.smtp_username, config.smtp_password)
    client.sendmail(config.smtp_username, recipient_list, message)
    client.close()


def main():
    print("Fetching giveaways..")
    data = fetch_active_giveaways()
    
    print("Initialize database for use..")
    init_db()
    
    print("Filtering new giveaways..")
    filtered = filter_giveaways(data, True, config.min_value, config.max_value)

    if len(filtered) <= 0:
        print("No new giveaways detected. Exiting..")
        return

    print("Reading email recipients from file..")
    recs = get_mail_recipients()

    if len(recs) <= 0:
        print("No email recipients could be read. Exiting..")
        return

    print("Building email for new giveaways")
    message = build_email_message(filtered, recs)

    print("Sending mail to recipients..")
    send_email(recs, message)

    print("Inserting notified giveaways to db..")
    insert_giveaways(filtered)

    print("All done. Exiting..")
    return


if __name__ == "__main__":
    main()
