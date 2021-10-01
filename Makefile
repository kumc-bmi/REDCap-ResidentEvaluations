run: clean venv
	mkdir -p export/attachments
	. ./.secrets &&\
	. venv/bin/activate && \
	which python && \
	python download_redcap_data.py 'config_env_token.ini' '23431-GPC-breast-cancer-review-1-export-xml'

py2:
	# install python2 and creating python virtual env"
	conda create -y -n py2 python=2.7 
	#echo "run manually: conda activate py2"

venv: venv_clear
	pip install virtualenv
	python -m virtualenv venv && \
	. ./venv/bin/activate && \
	pip install --upgrade pip  && \
	pip install -r requirements.txt  && \
	pip freeze >  requirements_pip_freeze.txt  && \
	which pip && which python && python --version

venv_clear:
	# "deleting python virtual env"
	rm -rf venv
	
clean:
	rm -rf export

