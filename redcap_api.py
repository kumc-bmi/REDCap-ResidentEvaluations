import requests


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
