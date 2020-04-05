set -x
#/bin/bash setup.sh
echo "" >>.secrets
echo "Have you added your secret api in .secret file ??? Dont version controlled secrets"
source .secrets
python2 download_redcap_data.py 'config_env_token.ini' '16558-COVID-19-ICU-surge-capacity-survey'
