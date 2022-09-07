from google.cloud import storage, bigquery
#import json
import pandas as pd
import io


# def upload_blob(source_bucket_name, source_blob, destination_bucket, destination_blob, context):
#   # *** Upload a file to the bucket ***
#   storage_client = storage.Client()
#   source_bucket_name = storage_client.get_bucket(bucket_name)
#   blob = bucket.blob(destination_blob_name)
#   blob.upload_from_string(blob_text)
#   print('File {}uploaded to bucket {}'.format(destination_blob_name,bucket_name))

def cloud_function(event, context):
  if  ('.csv' in event['name']):
    storage_client = storage.Client()
    source_bucket_name = storage_client.bucket(event['bucket'])
    source_blob = source_bucket_name.blob(event['name'])
    destination_blob_name = event['name']
    #destination_name = 'cold-bucket-12345'
    destination_name = "ny-rides-horlad-output"
    data = source_blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(data))
    print(df.shape)
    df['new_column'] = 1
    df.to_csv(f'gs://{destination_name}/{destination_blob_name}', index=False)

    
    #destination_bucket_name = storage_client.bucket(destination_name)
    #destination_blob = destination_bucket_name.blob(destination_blob_name)
    #EVENT = json.dumps(event)

    #upload_blob(BUCKET_NAME, BLOB_NAME, context)


# import pandas as pd
# from pandas.io import gbq
# from io import BytesIO, StringIO
# import numpy as np
# import io


def hello_pubsub(event, context):
  client = bigquery.Client()

  # TODO(developer): Set table_id to the ID of the table to create.
  table_id = "ny-rides-horlad.dataprep.test_trigger"
  print(event)

  job_config = bigquery.LoadJobConfig(autodetect=True,
  write_disposition=bigquery.job.WriteDisposition.WRITE_TRUNCATE)
    
    
    # time_partitioning=bigquery.TimePartitioning(
    #     type_=bigquery.TimePartitioningType.DAY,
    #     field="date",  # Name of the column to use for partitioning.
    #     expiration_ms=7776000000,  # 90 days.
    # ))
  uri = "gs://ny-rides-horlad-output/test_trigger.csv"

  load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
      # Make an API request.

  load_job.result()  # Waits for the job to complete.

  destination_table = client.get_table(table_id)  # Make an API request.
  print("Loaded {} rows.".format(destination_table.num_rows))
# def hello_gcs(event, context):
#     print('Event ID:', context.event_id)
#     print('Event Type:', context.event_type)
#     print('Bucket', event['bucket'])
#     print('File:', event['name'])
#     print('Metageneration:', event['metageneration'])
#     print('Created:', event['timeCreated'])
#     print('Updated:', event['updated'])