import os
from sys import argv
from smtplib import SMTP
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


def send_email(from_email, to_email, subject, body_text, file_path, smtp_server):


    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(body_text))

    with open(file_path, "rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=file_path
        )
    filename = os.path.basename(file_path)
    # After the file is closed
    part['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    msg.attach(part)

    smtp = SMTP(smtp_server)
    smtp.sendmail(from_email, to_email, msg.as_string())
    print ("Sent report to: {}".format(to_email))
    smtp.close()


if __name__ == "__main__":
    [from_email, to_email, subject,
     body_text, file_path, smtp_server] = argv[1:]
    send_email(from_email, to_email, subject,
                body_text, file_path, smtp_server)
