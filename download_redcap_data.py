import ConfigParser


def make_redcap_api_call(redcap_api_url, data, logging, post):
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
        response = post(redcap_api_url, data)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception('%s - %s' %
                            (response.status_code, response.content))

    except Exception as e:
        logging.error("""
            redcap rest call was unsuccessful
            or target server is down/ check configuration
            %s
            """ % (e))

            
def read_config(config_file, logging, Path):
       
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.readfp(Path(config_file).open(), str(config_file))

    sections = [section for section in config.sections()]
    logging.info("availabe configs: %s" % (sections))
    
    return config


def main(config_file, pid, logging, post, join, environ, Path):
    
    # read config file
    config = read_config(config_file, logging, Path)
    
    # parse config
    redcap_api_url = config._sections['global']['redcap_api_url']
    request_payload = dict(config.items(pid))
    
    # reading key from environment variable and replace string with key
    request_payload['token'] = environ[request_payload['token']]

    # send request to redcap
    data_string = make_redcap_api_call(
        redcap_api_url, request_payload, logging, post)

    # creating export path and filename
    export_filename = request_payload['export_filename']
    export_path = request_payload['export_path']
    full_path = join(export_path, export_filename)

    # exporting to file
    full_path = Path(full_path)
    full_path.write_bytes(data_string)

    logging.info("File has been downloaded at %s ." % (full_path))


if __name__ == "__main__":

    def _main_ocap():
        '''
        # https://www.madmode.com/2019/python-eng.html
        '''

        import logging
        from requests import post
        from os import environ
        from os.path import join
        from sys import argv
        from pathlib2 import Path

        logging.basicConfig(level=logging.DEBUG)

        if len(argv) != 3:
            logging.error("""Wrong format or arguments :
             please try like 'python download_recap_data.py config_file pid""")
        
        [config_file, pid] = argv[1:]
        main(config_file, pid, logging, post, join, environ, Path)

    _main_ocap()
