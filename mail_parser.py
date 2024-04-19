import imaplib
import email
import yaml
import json

# loading the credentials.yml file
with open("credentials.yml") as f:
    content = f.read()

# loading the contents of the file
my_credentials = yaml.load(content, Loader=yaml.FullLoader)
# fetching the user and password using exact keywords
user, password = my_credentials["user"], my_credentials["password"]

# URL for imap connection
imap_url = 'imap.gmail.com'

# Connection to Gmail using SSL
my_mail = imaplib.IMAP4_SSL(imap_url)

# Log in using your credentials
my_mail.login(user, password)

# Select the inbox to fetch messages
my_mail.select('Inbox')

emails = ['mail1','mail2','mail3'] #mail ids whose mails you want to parse
parsed_mails = []  # List to store parsed emails

# These are modifications to simplify search
# we can define "value" which is the mail id whose emails we want to parse through
for mail_id in emails:
    key = 'FROM'
    value = mail_id
    _, data = my_mail.search(None, key, value) #(None,'UNSEEN',key,value) to parse through only unread mails

    # data variable is a list of numbers that represents the mail id of the mails received from 'value' amongst all mails in the inbox
    mail_id_list = data[0].split()

    msgs = []  # empty list to capture all messages

    for num in mail_id_list:
        typ, data = my_mail.fetch(num, '(RFC822)')  # to extract every part of the message including the body and header
        msgs.append(data)

    '''
    In a multipart email, email.message.Message.get_payload() returns a list with one item for each part
    The easiest way is to walk the message and get the payload on each part
    '''
    # Note that each message has

    for msg in msgs[::-1]:
        for response_part in msg:
            if isinstance(response_part, tuple):
                my_msg = email.message_from_bytes(response_part[1])
                subject = my_msg['subject']
                body = ""

                if my_msg.is_multipart():
                    for part in my_msg.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            body += part.get_payload(decode=True).decode()
                else:
                    body = my_msg.get_payload(decode=True).decode()

                parsed_email = {
                    "subject": subject,
                    "body": body.strip()
                }

                # Store each parsed email dictionary in the list
                parsed_mails.append(parsed_email)

# Print or use parsed emails as needed

with open('parsed_mails.json', 'w') as json_file:
    json.dump(parsed_mails, json_file)

my_mail.close()
my_mail.logout()
