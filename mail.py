import base64
import email
import imaplib
import json
import math
import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from crypt import Tree


class Sender:
    def __init__(self,email, password):
        self.email = email
        self.password = password
        if email.split('@')[1]=='google.com':
            self.server = smtplib.SMTP("smtp.gmail.com", 587)
        elif email.split('@')[1]=='yandex.ru':
            self.server = smtplib.SMTP('smtp.yandex.ru', 25)
        elif email.split('@')[1]=='rambler.ru':
            self.server = smtplib.SMTP('smtp.rambler.ru', 25)
        self.server.starttls()
        try:
            self.server.login(email, password)
        except Exception as e:
            raise e

    def send_encrypted_email(self, email_to, subject, text):
        a = text
        dict_count_s = {i: subject.count(i) for i in set(subject)}
        dict_count_s = dict(sorted(dict_count_s.items(), key=lambda x: x[1], reverse=True))
        dict_count_frequency_s = {i: [subject.count(i), round(subject.count(i) / len(subject), 4)] for i in set(subject)}
        tree_s = Tree(dict_count_s, subject)
        tree_s.get_code()
        subject = tree_s.encrypt()
        with open('subject_code.json', 'w') as f:
            json.dump(tree_s.char_coded, f)

        dict_count_t= {i: text.count(i) for i in set(text)}
        dict_count_t = dict(sorted(dict_count_t.items(), key=lambda x: x[1], reverse=True))
        dict_count_frequency_t = {i: [text.count(i), round(text.count(i) / len(text), 4)] for i in
                                  set(text)}

        tree_t = Tree(dict_count_t, text)
        tree_t.get_code()
        with open('text_code.json', 'w') as f:
            json.dump(tree_t.char_coded, f)
        text = tree_t.encrypt()

        msg = MIMEMultipart()
        text_msg = MIMEText(text, 'plain')
        msg.attach(text_msg)
        part = MIMEBase('aplication', 'octet-stream')
        part.set_payload(open('subject_code.json', 'rb').read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename="subject_code.json")

        msg.attach(part)

        part = MIMEBase('aplication', 'octet-stream')
        part.set_payload(open('text_code.json', 'rb').read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename="text_code.json")
        msg.attach(part)

        msg['Subject'] = subject
        # print(dict_count_frequency_s, dict_count_frequency_t, sep='\n')
        self.server.sendmail(self.email, email_to, msg.as_string())
        compression_ratio = 0
        for i in tree_t.char_coded:
            compression_ratio += len(tree_t.char_coded[i])*dict_count_t[i]
        self.bytes_after_compression = math.ceil(compression_ratio / 8)
        self.coefficient = round(len(a) / self.bytes_after_compression, 2)
        os.remove('subject_code.json')
        os.remove('text_code.json')

    def letters_received(self):
        if self.email.split('@')[1] == 'google.com':
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
        elif self.email.split('@')[1] == 'yandex.ru':
            mail = imaplib.IMAP4_SSL('imap.yandex..ru')
        elif self.email.split('@')[1] == 'rambler.ru':
            mail = imaplib.IMAP4_SSL('imap.rambler.ru')

        mail.login(self.email, self.password)
        mail.list()
        mail.select('inbox')

        result, data = mail.search(None, "ALL")
        ids = data[0]
        id_list = ids.split()
        mails_body = []
        for i in id_list:
            each_mail_body = []
            latest_email_id = i
            result, data = mail.fetch(latest_email_id, "(RFC822)")
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')

            email_message = email.message_from_string(raw_email_string)
            each_mail_body.append(email.utils.parseaddr(email_message['From']))
            subject = 'нет темы'
            if email_message['Subject']:
                subject = email_message['Subject'].strip()
            each_mail_body.append(subject)
            if email_message.is_multipart():
                body = ""
                for payload in email_message.get_payload()[:len(email_message.get_payload()) - 1]:
                    try:
                        body += payload.get_payload(decode=True).decode('utf-8')
                    except:
                        pass
            else:
                body = email_message.get_payload(decode=True).decode('utf-8')
            # print(body)
            each_mail_body.append(body)
            each_mail_body.append(email_message)
            mails_body.append(each_mail_body)

        return mails_body

    def get_files(self, email_message):
        files = []
        for part in email_message.walk():
            filename = part.get_filename();
            if 'application' in part.get_content_type():
                filename = part.get_filename()
                transfer_encoding = part.get_all('Content-Transfer-Encoding')
                if transfer_encoding and transfer_encoding[0] == 'base64':
                    filename_part = filename.split('?')
                    try:
                        filename = base64.b64decode(filename_part[3]).decode(filename_part[1])
                    except:
                        pass
            if filename:
                fp = open(filename, 'wb')
                fp.write(part.get_payload(decode=1))
                fp.close()
                files.append(filename)
        return files

