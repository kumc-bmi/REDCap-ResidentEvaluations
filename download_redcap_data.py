import requests
import ConfigParser
from os import environ
from os.path import join
from sys import argv


def make_redcap_api_call(redcap_api_url, data):
    """

    >>> make_redcap_api_call(redcap_api_url='https://redcap.kumc.edu/api/', data = { \
        'content' : 'exportFieldNames' \
        ,'format' : 'json' \
        ,'returnFormat' : 'json' \
        ,'field' : 'email_id' \
        ,'token' : 'token' \
        })
    '[{"original_field_name":"email_id","choice_value":"","export_field_name":"email_id"}]'
    """

    try:
        response = requests.post(redcap_api_url, data)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception('%s - %s' %
                            (response.status_code, response.content))

    except Exception as e:
        print """
            redcap rest call was unsucessful
            or target server is down/ check configuration
            %s
            """ % (e)

            
def read_config(config_file):
       
    config = ConfigParser.ConfigParser()
    config.optionxform=str
    config.readfp(open(config_file)) 

    sections = [section for section in config.sections()]
    print ("availabe configs: %s" %(sections))
    
    return config


def main(config_file,pid):
    
    # read config file
    config = read_config(config_file)
    

    # parse config 
    redcap_api_url = config._sections['global']['redcap_api_url']
    request_payload = dict(config.items(pid))
    
    #reading key from enviornment variable and replace string with key
    request_payload['token'] = environ[request_payload['token']]

    #send request to redcap
    data_string = make_redcap_api_call(redcap_api_url,request_payload)

    # creating export path and filename
    export_filename = request_payload['export_filename']
    export_path = request_payload['export_path']
    full_path = join(export_path,export_filename)
    print (full_path)

    #exporting to file
    with open(full_path,'w') as file:
        file.write(data_string)


if __name__ == "__main__":
    if len(argv) != 3:
        print ("""
                Wrong format or arguments
                please try like 'python download_recap_data.py config_file pid'
               """)
    
    [config_file, pid] = argv[1:]
    main(config_file, pid)
