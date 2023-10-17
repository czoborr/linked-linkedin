import pandas as pd
import numpy as np
import json

JSON = open('linkedin_data.json')

# Load JSON data from a file into a DataFrame
file_path = 'path_to_your_json_file.json' #Insert path
df = pd.read_json('linkedin_data.json')

df = df.replace(to_replace='None', value=np.nan).dropna()

df['country'] = df['company_location'].apply(lambda x: x.split(',')[-1])
df['city'] = df['company_location'].apply(lambda x: x.split(',')[0])
df['unit'] = df['post_date'].apply(lambda x: x.split(' ')[0]).astype(int)
df['time_unit'] = df['post_date'].apply(lambda x: x.split(' ')[1])
df['applicants'] = df['applicant_number'].apply(lambda x: x.split(' ')[-2]).astype(int)
df['posted_days'] = np.where(df['time_unit'].str.lower().str.contains('hour'), df.unit / 24,
                             np.where(df['time_unit'].str.lower().str.contains('week'), df.unit * 7,
                                      np.where(df['time_unit'].str.lower().str.contains('month'), df.unit * 30,
                                               np.where(df['time_unit'].str.lower().str.contains('day'), df.unit,
                                                        1 / 24))))
df['job_title_clean'] = np.where(df['job_title'].str.contains('Analyst') | df['job_title'].str.contains('Analytics')
                                 | df['job_title'].str.contains('Analysis'), 'Data Analyst',
                                 (np.where(df['job_title'].str.contains('Scientist') | df['job_title'].str.contains(
                                     'Science'), 'Data Scientist',
                                           (np.where(df['job_title'].str.contains('Engineer'), 'Engineer',
                                                     (np.where(df['job_title'].str.contains('BI') | df[
                                                         'job_title'].str.contains('Business Intelligence'), 'BI',
                                                               'Other')))))))

df['SQL'] = np.where(df['job_description'].str.contains('SQL'), 1, 0)
df['Python'] = np.where(df['job_description'].str.lower().str.contains('python'), 1, 0)
df['Spark or Hive'] = np.where(
    df['job_description'].str.lower().str.contains('spark') | df['job_description'].str.lower().str.contains('hive'), 1,
    0)
df['PowerBI'] = np.where(
    df['job_description'].str.lower().str.contains('powerbi') | df['job_description'].str.lower().str.contains(
        'power bi'), 1, 0)
df['Scikit-learn'] = np.where(
    df['job_description'].str.lower().str.contains('scikit') | df['job_description'].str.lower().str.contains(
        'sklearn'), 1, 0)
df['Tableau'] = np.where(df['job_description'].str.lower().str.contains('tableau'), 1, 0)
df['BigData'] = np.where(df['job_description'].str.lower().str.contains('big data'), 1, 0)
df['ML'] = np.where(
    df['job_description'].str.lower().str.contains('machine learning') | df['job_description'].str.contains('ML') | df[
        'job_description'].str.lower().str.contains('deep learning'), 1, 0)
df['ETL'] = np.where(df['job_description'].str.contains('ETL'), 1, 0)
df['ABtest'] = np.where(df['job_description'].str.contains('A/B'), 1, 0)
df['Senior'] = np.where(df['job_title'].str.lower().str.contains('senior'), 1, 0)
df['Remote'] = np.where(df['job_description'].str.lower().str.contains('remote'), 1, 0)

df.to_csv('Cleaned_Data.csv')
