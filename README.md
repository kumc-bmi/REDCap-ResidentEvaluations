# REDCap-ResidentEvaluations

## Install python environment (one time)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda create -n py2 python=2.7
source activate py2
conda install virtualenv
virtualenv env

## Activate python environment
. env/bin/activate
pip install -r requirements.txt 

## create directories
rm -rf export
mkdir -p export/attachments

## edit config file
Take look examples at config_env_token.ini . Never stored token in config file, instead use environment variable. 

download_redcap_data.py is pretty flexible, you can pass all payload request parameters from https://redcap.kumc.edu/redcap_v8.5.24/API/playground.php?pid=XYZ.

Example: I have created a report in redcap project, and I want download that report as csv. Go to the above link of the project. You will find redcap will help you create following parameters. Keep in mind token_8693 is not real token, it is stored in env vairable.

token: token_8693
content: report
format: csv
report_id: 25105
rawOrLabel: label
rawOrLabelHeaders: raw
exportCheckboxLabel: true
returnFormat: json

Just copy all the parameter, add title, description, export_filename, export_path like:

[8693-resident-eval-31-days]
description: This is resident evaluation export (ticket:5569)
export_filename: 8693-resident-eval-31-days.csv
export_path: ./export
token: token_8693
content: report
format: csv
report_id: 25105
rawOrLabel: label
rawOrLabelHeaders: raw
exportCheckboxLabel: true
returnFormat: json

## Downlod data
python download_redcap_data.py 'config_env_token.ini' '8693-resident-eval-183-days'

## To Send email
python send_email.py $from_email $to_email $subject $body_text $file_path $smtp_server

## Resident Evaluation (https://bmi-work.kumc.edu/work/ticket/5569)
Upto this all code was generic, and can be used by any redcap project. From now on code is for resident evaluation project only.

src_data='export/8693-resident-eval-183-days.csv'
attachment_export_dir='export/attachments/'
from_email='misupport@kumc.com'
subject='EvaluationSummary'
smtp_server=smtp.kumc.edu
body_text='Attached is a CSV report of all of the evaluations done on your work in the last month. '

python monthly_res_eval.py $src_data $attachment_export_dir $from_email  "${subject}" $smtp_server "${body_text}"

