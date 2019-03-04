from json import loads
import calendar
import operator
import csv
from datetime import datetime  # for strptime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


# Function for making api call
def api(url, data, post):
    req = post(url, data)
    return loads(req.content)


# Send email
def send_report(from_email, to_email, file_path, cwd, SMTP):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = file_path.splitext()[0]

    text = "Attached is a CSV document containing evaluations done on you during the last month. " \
           "\n\nThank you,\nMISupport"

    msg.attach(MIMEText(text))

    with file_path.open("rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=file_path.name
        )
        # After the file is closed
    part['Content-Disposition'] = 'attachment; filename="%s"' % file_path.name
    msg.attach(part)

    smtp = SMTP('smtp.kumc.edu')
    smtp.sendmail(from_email, to_email, msg.as_string())
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
    days_in_month = calendar.monthrange(cur_date.year, cur_date.month)[1]

    # Iterate through resident evaluations
    for res_eval in evals:
        res_email = res_eval['resident_email']
        res_eval_date = res_eval['date_of_surgery']
        datetm = datetime.strptime(res_eval_date, "%Y-%m-%d")

        # If the date of the surgery being evaluated happens in the last month, add that eval to the list to be exported
        if (datetime.datetime.now() - datetm).days <= days_in_month:
            resident_evals[res_eval['record_id']] = res_email

    return resident_evals


# Sort evaluations by resident, generate CSV, and store it in the temp directory
def generate_reports(evals, fields_to_export, api_con, cur_date, cwd, post):
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
def queue_emails(from_email, emails_and_files, cwd, SMTP):
    for ef in emails_and_files.keys():
        send_report(from_email, ef, emails_and_files[ef], cwd, SMTP)

    for ef in emails_and_files.keys():
        emails_and_files[ef].remove()


def main(argv, cwd, now, post, SMTP):
    # api_con = (api_url, api_key)
    api_con = (argv[1], argv[2])

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

    fields_to_export = ('resident_email', 'resident_kumc', 'training_year', 'rotation_kumc', 'surgery', 'second_surgery', 'complexity',
                      'pre_procedure_plan', 'steps', 'technical_performance', 'visuospatial_skills_instru',
                      'post_procedure_plan', 'communication', 'case_performed', 'critical_maneuvers',
                      'resident_is_able_to_safely', 'done_well', 'needs_improvement', 'real_time_eval')

    from_email = "misupport@kumc.edu"

    evals = api(api_con[0], data, post)
    cur_date = now()
    resident_evals = get_residents(evals, cur_date)

    emails_and_files = generate_reports(resident_evals, fields_to_export, api_con, cur_date, cwd, post)
    queue_emails(from_email, emails_and_files, cwd, SMTP)


if __name__ == "__main__":
    def _script():
        import requests
        from sys import argv
        from smtplib import SMTP
        from datetime import datetime
        from pathlib import Path

        cwd = Path('.')
        main(argv, cwd, datetime.now, requests.post, SMTP)

    _script()
