set -x
# rm -rf export
mkdir -p export/attachments

virtualenv env
source env/bin/activate

pip2 install --upgrade pip
pip2 install -r requirements.txt
pip2 freeze >requirements_pip_freeze.txt

which python2
which pip2
