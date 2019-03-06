r"""monthly_res_eval - distribute evaluation reports

It's spring 2019 and resident Rich performed surgery 5 days ago:

    >>> resident_email = 'rich@g.com'
    >>> now = lambda: datetime(2019, 03, 14, 1, 1, 1)
    >>> date_of_surgery = now() - timedelta(days=5)

It's time to send evaluations for the month, so we run this script,
giving it API access to the REDCap project:

    >>> argv = 'script https://redcap/api api_key smtp.test.com mifake@url.com email text'.split()
    >>> io = MockIO(now, resident_email, date_of_surgery)
    >>> main(argv, io.environ, io.cwd, now, io.post, io.SMTP)
    1 evaluations found to send
    Sent report to: rich@g.com

Now we can see that a CSV file got sent to Rich:

    >>> for from_addr, to_addr, msg in io.smtp.sent:
    ...     print from_addr, to_addr
    ...     filename = msg.split('filename=')[1]
    ...     filename = filename.split('\n')[0]
    ...     print filename
    mifake@url.com rich@g.com
    "Evaluation_Summary_3_2019_rich.csv"

"""

from json import loads, dumps
import operator
import csv
from datetime import (
    timedelta,
    datetime  # for strptime
)
from pathlib import PosixPath
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


# Function for making api call
def api(url, data, post):
    req = post(url, data)
    return loads(req.content)


# Send email
def send_report(from_email, to_email, file_path, cwd, SMTP, smtp_server, text):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = file_path.splitext()[0]

    msg.attach(MIMEText(text))

    with file_path.open("rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=file_path.name
        )
        # After the file is closed
    part['Content-Disposition'] = 'attachment; filename="%s"' % file_path.name
    msg.attach(part)

    smtp = SMTP(smtp_server)
    smtp.sendmail(from_email, to_email, msg.as_string())
    print "Sent report to: {}".format(to_email)
    smtp.close()


# function for generating CSV
def add_to_csv(title, content, fields_to_export, cwd):
    csv_file = cwd / "{}.csv".format(title)

    file_exists = False

    if csv_file.isfile():
        file_exists = True

    with csv_file.open('a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')

        # label row, only if file doesn't exist
        if file_exists:
            pass
        else:
            filewriter.writerow(fields_to_export)

        for row in content:
            line = []
            row_dict = dict(row)

            for field in fields_to_export:
                key = str(field).replace("'", "")
                value = row_dict[key].encode('utf-8')
                line.append(value.replace("\n", "").replace("\r", ""))

            # check for empty lines
            empty = 0
            for val in line:
                if val == '':
                    empty = empty + 1

            if empty != len(line):
                filewriter.writerow(line)
    return csv_file


# Retrieve residents from whole project, who have had a surgery evaluation in the last month
def get_residents(evals, cur_date):
    resident_evals = {}

    # Iterate through resident evaluations
    for res_eval in evals:
        res_email = res_eval['resident_email']
        res_eval_date = res_eval['date_of_surgery']
        datetm = datetime.strptime(res_eval_date, "%Y-%m-%d")

        if (cur_date - datetm).days <= 31:
            resident_evals[res_eval['record_id']] = res_email

    return resident_evals


def generate_reports(evals, fields_to_export, api_con, cur_date, cwd, post):
    """Sort evaluations by resident, generate CSV, and store it in the temp directory

    >>> now = lambda: datetime(2001, 1, 2, 3, 4, 5, 6)
    >>> io = MockIO(now, 'rich@g.com', now())
    >>> generate_reports({'resident_email': 'rich@g.com'},
    ...                  [], ('x', 'y'), now(),
    ...                  io.cwd, io.post)
    {'rich@g.com': MockPath('Evaluation_Summary_1_2001_rich.csv')}
    """
    sorted_evals = sorted(evals.items(), key=operator.itemgetter(1))
    emails_and_files = {}

    for res_eval in sorted_evals:
        eval = get_eval(res_eval, api_con, post)

        resident_id = res_eval[1].split("@")[0]
        title = "Evaluation_Summary_{}_{}_{}".format(cur_date.month, cur_date.year, resident_id)

        csv_file = add_to_csv(title, eval, fields_to_export, cwd)
        emails_and_files[res_eval[1]] = cwd / "{}.csv".format(title)

    return emails_and_files


# Get evaluation info via API
def get_eval(res_eval, api_con, post):
    data = {
        'token': api_con[1],
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'records[0]': res_eval[0],
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }

    return api(api_con[0], data, post)


# queue emails, and delete files
def queue_emails(from_email, emails_and_files, cwd, SMTP, smtp_server, text):
    for ef in emails_and_files.keys():
        send_report(from_email, ef, emails_and_files[ef], cwd, SMTP, smtp_server, text)

    for ef in emails_and_files.keys():
        emails_and_files[ef].remove()


class REProject(object):
    fields_to_export = ('resident_email', 'resident_kumc', 'training_year', 'rotation_kumc', 'surgery', 'second_surgery', 'complexity',
                      'pre_procedure_plan', 'steps', 'technical_performance', 'visuospatial_skills_instru',
                      'post_procedure_plan', 'communication', 'case_performed', 'critical_maneuvers',
                      'resident_is_able_to_safely', 'done_well', 'needs_improvement', 'real_time_eval')


def main(argv, environ, cwd, now, post, SMTP):
    [api_url, api_key_var, smtp_server, from_email, text] = argv[1:6]
    api_con = (api_url, environ[api_key_var])

    data = {
        'token': api_con[1],
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }

    evals = api(api_con[0], data, post)
    cur_date = now()
    resident_evals = get_residents(evals, cur_date)

    emails_and_files = generate_reports(resident_evals, REProject.fields_to_export, api_con, cur_date, cwd, post)
    print "{} evaluations found to send".format(emails_and_files.__len__())
    queue_emails(from_email, emails_and_files, cwd, SMTP, smtp_server, text)


class MockIO(object):

    environ = {"api_key": "SUPERSEKRET"}

    def __init__(self, now, resident_email, date_of_surgery):
        fields = {f: 'junk'
                  for f in REProject.fields_to_export}
        self.eval1 = dict(
            fields,
            record_id='123',
            resident_email=resident_email,
            date_of_surgery=date_of_surgery.strftime("%Y-%m-%d"))

        self.cwd = MockPath('.')
        self.cur_date = now()
        self.smtp = None

    def __repr__(self):
        return 'MockIO(%s)' % self.cur_date.strftime("%Y-%m-%d")

    def post(self, url, data):
        return self

    @property
    def content(self):
        return dumps([self.eval1])

    def SMTP(self, server):
        self.smtp = MockSMTP(server)
        return self.smtp


class MockSMTP(object):
    def __init__(self, server):
        self.sent = []

    def sendmail(self, from_email, to_email, msg):
        self.sent.append((from_email, to_email, msg))

    def close(self):
        pass


class MockPath(PosixPath):
    def isfile(self):
        return False

    def open(self, mode='r'):
        from io import BytesIO
        return BytesIO()

    def splitext(self):
        return self.name.rsplit('.', 1)

    def remove(self):
        pass


if __name__ == "__main__":
    def _script():
        import requests
        from sys import argv
        from os import environ
        from smtplib import SMTP
        from datetime import datetime
        from pathlib import Path

        cwd = Path('.')
        main(argv, environ, cwd, datetime.now, requests.post, SMTP)

    _script()
