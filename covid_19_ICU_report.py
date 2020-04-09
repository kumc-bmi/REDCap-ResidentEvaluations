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

import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None


def map_recordid_to_sit(df):
    record_id_site = df[['record_id', 'site', 'site_oth']]
    record_id_site.site_oth = record_id_site.site_oth.replace(
        np.nan, '', regex=True)
    record_id_site.site = record_id_site.site + " " + record_id_site.site_oth
    del record_id_site['site_oth']
    record_id_site = record_id_site[record_id_site.site.notnull()].sort_values(
        'record_id')
    return record_id_site


def get_surge_data(df):
    surge_cols = ['site', 'record_id', 'icu_bed_num',
                  'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']
    df.site_oth = df.site_oth.replace(np.nan, '', regex=True)
    df.site = df.site + " " + df.site_oth
    latest_survey_by_site = df.groupby(['site']).dte_assessed.max()
    latest_survey_by_site = pd.DataFrame(latest_survey_by_site).reset_index()
    latest_df = latest_survey_by_site.merge(
        df, how='left', on=['site', 'dte_assessed'])
    surge_export_df = latest_df[surge_cols]  # 'site_id'
    return surge_export_df


def get_census_data(df):
    census_cols = ['record_id', 'redcap_repeat_instrument', 'redcap_repeat_instance',
                   'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent']

    census = df[df.redcap_repeat_instance.notnull()][census_cols]
    latest_record = pd.DataFrame(census.groupby(['record_id'])[
                                 'redcap_repeat_instance'].max()).reset_index()
    census = latest_record.merge(
        census, on=['record_id', 'redcap_repeat_instance']).sort_values(['record_id'])
    return census


df = pd.read_csv('export/16558-COVID-19-ICU-surge-capacity-survey.csv')
record_id_site = map_recordid_to_sit(df)
surge = get_surge_data(df)
census = get_census_data(df)

exit(0)
surge
# 1 instane for each site
# if more than one, ask to fix it. failed the report and send email. Is there way to notify ?

census
# more than 1 record per site
# take latest of redcap_repeat_instance

surge_census = surge.merge(census, on='record_id', how='left')
output_col_orders = ['site', 'record_id',
                     'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent',
                     'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']
surge_census = surge_census[output_col_orders]
surge_census.to_excel(
    'export/covid_surge_cenus_redcap_report.xlsx', index=False)

census = census.merge(record_id_site, on='record_id')
surge.merge(census, on='site', how='left',
            suffixes=('_x', ''))[output_col_orders]
#surge.join(census,on='site', how='left',rsuffix='_r')

