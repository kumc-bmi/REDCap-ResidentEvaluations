import requests
import datetime
import json
import calendar
import sys
import operator
import csv
import os.path

# Function for making api call
def api(url, data):
    req = requests.post(url, data)
    return json.loads(req.content)


# function for generating CSV
def add_to_csv(title, content, fields_to_export):
    csv_file = "{}.csv".format(title)

    file_exists = False

    if os.path.isfile(csv_file):
        file_exists = True

    with open(csv_file, 'a') as csvfile:
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
def get_residents(evals):
    resident_evals = {}
    cur_date = datetime.datetime.now()
    days_in_month = calendar.monthrange(cur_date.year, cur_date.month)[1]

    # Iterate through resident evaluations
    for res_eval in evals:
        res_email = res_eval['resident_email']
        res_eval_date = res_eval['date_of_surgery']
        datetm = datetime.datetime.strptime(res_eval_date, "%Y-%m-%d")

        # If the date of the surgery being evaluated happens in the last month, add that eval to the list to be exported
        if (datetime.datetime.now() - datetm).days <= 1000: # <CHANGE_ME - 1000 only for testing> days_in_month:
            resident_evals[res_eval['record_id']] = res_email

    return resident_evals


# Sort evaluations by resident, generate CSV, and store it in the temp directory
def generate_reports(evals, fields_to_export, api_con):
    sorted_evals = sorted(evals.items(), key=operator.itemgetter(1))

    for res_eval in sorted_evals:
        eval = get_eval(res_eval, api_con)

        cur_date = datetime.datetime.now()
        resident_id = res_eval[1].split("@")[0]
        title = "Evaluation_Summary_{}_{}_{}".format(cur_date.month, cur_date.year, resident_id)

        csv = add_to_csv(title, eval, fields_to_export)
        print csv


# Get evaluation info via API
def get_eval(res_eval, api_con):
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

    return api(api_con[0], data)


def main():
    # api_con = (api_url, api_key)
    api_con = (sys.argv[1], sys.argv[2])

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

    fields_to_export = ('resident_kumc', 'training_year', 'rotation_kumc', 'surgery', 'second_surgery', 'complexity',
                      'pre_procedure_plan', 'steps', 'technical_performance', 'visuospatial_skills_instru',
                      'post_procedure_plan', 'communication', 'case_performed', 'critical_maneuvers',
                      'resident_is_able_to_safely', 'done_well', 'needs_improvement', 'real_time_eval')

    evals = api(api_con[0], data)
    resident_evals = get_residents(evals)

    generate_reports(resident_evals, fields_to_export, api_con)


if __name__ == "__main__":
    main()

