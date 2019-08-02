import re
import os
import pandas as pd
import numpy as np
from sys import argv
from send_email import send_email


def create_email_name_filed(df):
    '''
    input : df
    output : df
    
    create coalesce email field using resident_sitename_kumc and  resident_email
    create colesce name field using resident_sitename
    
    '''
    df['email'] = np.nan
    df['email'] = df.email.fillna(df.resident_kumc_email
                         ).fillna(df.resident_amc_email
                         ).fillna(df.resident_slu_email
                         ).fillna(df.resident_evms_email
                         ).fillna(df.resident_wu_email
                         ).fillna(df.resident_uwm_email
                         ).fillna(df.resident_email
                         )

    df['name'] = np.nan
    df['name'] = df.name.fillna(df.resident_kumc
                       ).fillna(df.resident_amc
                       ).fillna(df.resident_slu
                       ).fillna(df.resident_evms
                       ).fillna(df.resident_wu
                       ).fillna(df.resident_uwm
                       )
    return df


def create_csv_attachments_per_email(df, attachment_export_dir):

    for unique_email in df.email.unique().tolist():
        df_per_email = (df[df.email == unique_email])

        filename = "EvaluationSummary_%s.csv" % (unique_email)
        path = os.path.join(attachment_export_dir, filename)
        df_per_email.to_csv(path, index=False)
        print ("File (%s) has been created" % (path))

    return 'created_csv_attachments'


def get_path_filename_email(folder):
    output = {}
    error_filenames = []
    for filename in os.listdir(folder):
        try:
            path = os.path.join(folder, filename)
            email = filename.split('.csv')[0].split('_')[1]
            output[path] = [filename, email]
        except:
            error_filenames.append(filename)
    print ("Following files have correct formate: %s \n" % (output.keys()))
    print ("Following files have wrong formate: %s \n" % (error_filenames))

    return output, error_filenames


def send_emails(attachment_export_dir, from_email, subject,
                body_text, smtp_server):
    '''
    1. get all attachments full path, filename, and email
    2. print full path
    3. find out which files will not be sent back
    4. 
    '''
    path_filename_email, error_filenames = get_path_filename_email(
        attachment_export_dir)

    for path in path_filename_email.keys():
        to_email = path_filename_email[path][1]
        send_email(from_email, to_email, subject,
                   body_text, path, smtp_server)
    
    if len(error_filenames)!=0:
        raise Exception(
            "Could not send email to following email address : %s " % (error_filenames))


def main(src_data, attachment_export_dir, from_email, subject,
         body_text, smtp_server):

    df = pd.read_csv(src_data, dtype=str)
    df = create_email_name_filed(df)

    create_csv_attachments_per_email(df, attachment_export_dir)
    send_emails(attachment_export_dir, from_email, subject,
                body_text, smtp_server)

if __name__ == "__main__":
    [src_data, attachment_export_dir, from_email, subject,
      smtp_server, body_text] = argv[1:]

    main(src_data, attachment_export_dir, from_email, subject,
         body_text, smtp_server)
