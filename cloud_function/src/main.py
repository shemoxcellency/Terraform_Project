def hello_gcs(event, context):
    print('Event ID:', context.event_id)
    print('Event Type:', context.event_type)
    print('Bucket', event['bucket'])
    print('File:', event['name'])
    print('Metageneration:', event['metageneration'])
    print('Created:', event['timeCreated'])
    print('Updated:', event['updated'])