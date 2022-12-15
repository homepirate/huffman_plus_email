import base64
import imaplib
import email
import os.path
import sys

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor


def get_files(email_message):
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
    print("________________")
    print(files)
    return files

mail = imaplib.IMAP4_SSL('imap.rambler.ru')
mail.login('gfgfga@rambler.ru', 'ABOBA!1135dd')
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
        # files = get_files(email_message)
        body =""
        for payload in email_message.get_payload()[:len(email_message.get_payload())-1]:
            try:
                body += payload.get_payload(decode=True).decode('utf-8')
            except:
                pass
    else:
        body = email_message.get_payload(decode=True).decode('utf-8')
    each_mail_body.append(body)
    each_mail_body.append(email_message)
    mails_body.append(each_mail_body)


print(mails_body)





def open_this_letter(index):
    button = QtWidgets.QApplication.instance().sender()
    print(button.text())

if __name__ == '__main__':
    layout = QtWidgets.QVBoxLayout()
    x = 50
    y = 10
    app = QtWidgets.QApplication(sys.argv)
    window = QWidget()
    window.resize(235, 300)
    window.setStyleSheet("background: #6ED0F6;\n"
"  color: #fff;\n"
"  font-family: \'Raleway\', sans-serif;\n"
"  -webkit-font-smoothing: antialiased;")
    mail_buttons = []
    for i, values in enumerate(mails_body[::-1][:5]):
        button = QtWidgets.QPushButton(f'{i+1}) From: {values[0][1]}\nSubject:{values[1][0:10]}')
        button.move(x, y)
        button.setStyleSheet("background: #079BCF;\n"
                                                "  border: none;\n"
                                                "  border-radius: 16px;\n"
                                                "  color: #fff;\n"
                                                "  cursor: pointer;\n"
                                                "  font-family: \'Raleway\', sans-serif;\n"
                                                "  font-size: 10px;\n"
                                                "  height: 50px;\n"
                                                "  width: 130%;\n"
                                                "  margin-bottom: 10px;\n"
                                                "  overflow: hidden;\n"
                                                "  transition: all .3s cubic-bezier(.6,0,.4,1);")
        button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        button.clicked.connect(lambda: open_this_letter(i))
        layout.addWidget(button)
        y += 70
        mail_buttons.append(button)

    window.setLayout(layout)
    window.show()
    print(mail_buttons)
    sys.exit(app.exec_())