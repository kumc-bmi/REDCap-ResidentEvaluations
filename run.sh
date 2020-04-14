set -x

#./setup.sh

rm -rf export
mkdir -p export/attachments

source env/bin/activate
which python2
which python3

echo "" >>.secrets
echo "Have you added your secret api in .secret file ??? Dont version controlled secrets"
source .secrets
python2 download_redcap_data.py 'config_env_token.ini' '16558-COVID-19-ICU-surge-capacity-survey'
python3 covid_19_ICU_report.py
