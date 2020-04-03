set -x
# rm -rf export
mkdir -p export/attachments
python3 -m venv env
source env/bin/activat
pip2 install -r requirements.txt
python2 download_redcap_data.py 'config_env_token.ini' '16558-COVID-19-ICU-surge-capacity-survey'
