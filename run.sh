set -x
/bin/bash setup.sh
source .env
python2 download_redcap_data.py 'config_env_token.ini' '16558-COVID-19-ICU-surge-capacity-survey'
