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


# Retrieve residents from whole project, who have had a surgery evaluation in the last month
def get_residents(evals):
    residents = {}
    cur_date = datetime.datetime.now()
    cur_month_days = calendar.monthrange(cur_date.year, cur_date.month)[1]

    # Iterate through resident evaluations
    for res_eval in evals:
        res_email = res_eval['resident_email']
        res_eval_date = res_eval['date_of_surgery']
        datetm = datetime.datetime.strptime(res_eval_date, "%Y-%m-%d")

        # If the date of the surgery being evaluated happens in the last month, add that eval to the list to be exported
        if (datetime.datetime.now() - datetm).days <= 1000: # <CHANGE_ME - 1000 only for testing> cur_month_days:
            residents[res_eval['record_id']] = res_email

    return residents


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
    residents = get_residents(evals)

    for key in residents.keys():
        print "{} - {}".format(key, residents[key])


if __name__ == "__main__":
    main()

