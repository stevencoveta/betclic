import pandas as pd 
from google.cloud import bigquery
from google.oauth2 import service_account

def upload_data_bq(table_id, df, append_truncate):

    data_types = {
        'object' : 'STRING',
        'int64' : 'INTEGER',
        'float64' : 'FLOAT',
        'bool' : 'BOOL',
        'datetime64' : 'DATETIME'
    }

    credentials = service_account.Credentials.from_service_account_file(
        "keyfile.json", scopes=["https://www.googleapis.com/auth/cloud-platform"]
                  )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id,)
  
    table_id = table_id
    columns = df.dtypes.replace(data_types)
    column_names = columns.index
    column_types = columns.values

    schema = []
    for column_name, column_type in zip(column_names, column_types):
        
        if column_type == 'STRING':
            schema.append(bigquery.SchemaField(column_name, column_type))
    
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition = append_truncate
    )

    job = client.load_table_from_dataframe(df,table_id, job_config=job_config)
    print('Uploading data to Bigquery...')
    job.result() 
    table = client.get_table(table_id) 
    print(
        "Loaded {} rows and {} columns to {}.".format(
            table.num_rows, len(table.schema), table_id
        )
    )

    print("data uploaded")

customer = pd.read_csv('datasets/CUSTOMER.csv', sep = ";")
daily_transaction = pd.read_csv('datasets/DAILY_TRANSACTION.csv', sep = ";")
ref_country = pd.read_csv('datasets/REFERENCE_COUNTRY.csv', sep = ";")
ref_country = ref_country[["CUSTOMER_COUNTRY_CODE","CUSTOMER_COUNTRY_LABEL"]]

destination = "bclic-371311.data.ref_country"

#upload_data_bq(destination,ref_country,'WRITE_TRUNCATE')
