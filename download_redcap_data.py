from redcap_api import make_redcap_api_call
import ConfigParser
from os import environ
from os.path import join


def read_config(config_file):
       
    config = ConfigParser.ConfigParser()
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
    main(config_file='config_env_token.ini',pid='8097')
    main(config_file='config_env_token.ini',pid='8097-ALL')
