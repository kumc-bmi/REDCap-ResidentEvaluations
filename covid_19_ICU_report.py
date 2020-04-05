# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import pandas as pd
import numpy as np

def map_recordid_to_sit(df):
    record_id_site = df[['record_id','site','site_oth']]
    record_id_site.site_oth = record_id_site.site_oth.replace(np.nan, '', regex=True)
    record_id_site.site = record_id_site.site + record_id_site.site_oth
    del record_id_site['site_oth']
    record_id_site = record_id_site[record_id_site.site.notnull()].sort_values('record_id')
    return record_id_site


def get_surge_data(df):
    surge_cols = ['site', 'record_id', 'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']
    df.site_oth = df.site_oth.replace(np.nan, '', regex=True)    
    df.site = df.site + df.site_oth
    latest_survey_by_site = df.groupby(['site']).dte_assessed.max()
    latest_survey_by_site = pd.DataFrame(latest_survey_by_site).reset_index()
    latest_df = latest_survey_by_site.merge(
        df, how='left', on=['site', 'dte_assessed'])
    surge_export_df = latest_df[surge_cols]  # 'site_id'
    return surge_export_df


def get_census_data(df):


    census_cols = ['record_id','redcap_repeat_instrument','redcap_repeat_instance',
                   'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent']

    census = df[df.redcap_repeat_instance.notnull()] [census_cols]
    latest_record = pd.DataFrame(census.groupby(['record_id'])['redcap_repeat_instance'].max()).reset_index()
    census = latest_record.merge(census,on=['record_id','redcap_repeat_instance']).sort_values(['record_id'])
    return census
# -

df = pd.read_csv('export/16558-COVID-19-ICU-surge-capacity-survey.csv')
record_id_site= map_recordid_to_sit(df)
surge = get_surge_data(df)
census = get_census_data(df)
surge_census = census.merge(record_id_site,on ='record_id')
output_col_orders= ['site', 'record_id', 
                    'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent'
                    'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']

surge_census[output_col_orders]

# +
surge


# -

census

#['covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent','noncovid_icu', 'noncovid_icu_vent']
surge_export_df.merge(census,on='site')

# +


results = pd.read_csv('export/out.txt', sep='\t').sort_values(['site'])
results = results[['site', 'site_id', 'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent',
                   'noncovid_icu', 'noncovid_icu_vent', 'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']]  # 'site_id'
# -

surge_export_df.join(census,on='site')

census.site.to_list()

surge_export_df.site.tolist()

surge_export_df.merge(census,how='left',on='site')



latest_export_df.to_csv('export/output_LP.csv', index=False)
results.to_csv('export/output_original.csv', index=False)

# # NEW method
#
#

# +
import pandas as pd

df = pd.read_csv('export/16558-COVID-19-ICU-surge-capacity-survey.csv')

# find relation before record_id and site
record_id_site = df[['record_id','site','site_oth']]
record_id_site.site = record_id_site.site + record_id_site.site_oth.astype(str)
del record_id_site['site_oth']
record_id_site = record_id_site[record_id_site.site.notnull()].sort_values('record_id')

# +
# find latest surge records and cols

census_cols = ['record_id','redcap_repeat_instrument','redcap_repeat_instance',
               'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent']

census = df[df.redcap_repeat_instance.notnull()] [census_cols]

latest_record = pd.DataFrame(census.groupby(['record_id'])['redcap_repeat_instance'].max()).reset_index()
census = latest_record.merge(census,on=['record_id','redcap_repeat_instance']).sort_values(['record_id'])

# +
# find surge records and cols
surge_cols =['record_id','site','site_oth','dte_assessed','redcap_repeat_instrument','redcap_repeat_instance',
             'noncovid_icu', 'noncovid_icu_vent', 'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']
surge = df[df.redcap_repeat_instance.isnull()] [surge_cols]
surge.site = surge.site + surge.site_oth.astype(str)

latest_surge_by_site = surge.groupby(['site']).dte_assessed.max()
latest_surge_by_site = pd.DataFrame(latest_surge_by_site).reset_index()
latest_df = latest_surge_by_site.merge(
    df, how='left', on=['site', 'dte_assessed'])
# -

latest_df

# +
census

census = census.join(record_id_site,on='record_id',lsuffix='', rsuffix='_s')
censud_cols = ['site'] + censud_cols

census = census[censud_cols].sort_values(['site','record_id'])
# census.site = census.site + census.site_oth.astype(str)

# census

# +
df_static = df [df.covidpend_icu_bed.notna()| \
df.covidpend_icu_bed_vent.notna()| \
df.covidcfrm_icu_bed.notna()| \
df.covidcfrm_icu_bed_vent.notna()| \
df.noncovid_icu.notna()| \
df.noncovid_icu_vent.notna()] 

static_data_cols = ['site', 'record_id','covidpend_icu_bed','covidpend_icu_bed_vent','covidcfrm_icu_bed','covidcfrm_icu_bed_vent','noncovid_icu','noncovid_icu_vent']
# -

static_data_cols

df_static[static_data_cols]

df.columns

results.columns.tolist()

df = pd.read_csv('export/16558-COVID-19-ICU-surge-capacity-survey.csv')







print(results.columns.tolist())



['site', 'site_id', 
 'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent', 
 'noncovid_icu', 'noncovid_icu_vent', 'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']


