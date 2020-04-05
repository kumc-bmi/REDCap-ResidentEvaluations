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

results = pd.read_csv('export/out.txt', sep='\t').sort_values(['site'])
results = results[['site', 'site_id', 'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent',
                   'noncovid_icu', 'noncovid_icu_vent', 'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']]  # 'site_id'

df = pd.read_csv('export/16558-COVID-19-ICU-surge-capacity-survey.csv')
df.site = df.site + df.site_oth.astype(str)
latest_survey_by_site = df.groupby(['site']).dte_assessed.max()
latest_survey_by_site = pd.DataFrame(latest_survey_by_site).reset_index()
latest_df = latest_survey_by_site.merge(
    df, how='left', on=['site', 'dte_assessed'])
latest_export_df = latest_df[['site', 'record_id', 'covidpend_icu_bed', 'covidpend_icu_bed_vent', 'covidcfrm_icu_bed', 'covidcfrm_icu_bed_vent',
                              'noncovid_icu', 'noncovid_icu_vent', 'icu_bed_num', 'ventilator_num', 'icu_bed_surge_num', 'ventilator_surge_num']]  # 'site_id'
# -

latest_export_df.to_csv('export/output_LP.csv', index=False)
results.to_csv('export/output_original.csv', index=False)
