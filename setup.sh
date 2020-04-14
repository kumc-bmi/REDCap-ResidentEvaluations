set -x

virtualenv env
source env/bin/activate

pip2 install --upgrade pip
pip2 install -r requirements.txt
pip2 freeze >requirements_pip_freeze.txt

pip3 install --upgrade pip
pip3 install -r requirements_pip3.txt
pip3 freeze >requirements_pip3_freeze.txt

which python2
which pip2
which python3
which pip3
