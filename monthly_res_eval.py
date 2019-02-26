import requests
import datetime
import json
import calendar
import sys


# Function for making api call
def api(url, data):
    req = requests.post(url, data)
    return json.loads(req.content)


# function for generating CSV
def create_csv():
    pass


def main():
    api_url = sys.argv[1]
    api_key = sys.argv[2]

    data = {
        'token': api_key,
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

    evals = api(api_url, data)

    cur_date = datetime.datetime.now()
    cur_month_days = calendar.monthrange(cur_date.year, cur_date.month)[1]

    for res_eval in evals:
        res_email = res_eval['resident_email']
        res_eval_date = res_eval['date_of_surgery']
        datetm = datetime.datetime.strptime(res_eval_date, "%Y-%m-%d")

        if (datetime.datetime.now() - datetm).days <= 200:
            # do export
            print res_email
            print res_eval_date


if __name__ == "__main__":
     main()