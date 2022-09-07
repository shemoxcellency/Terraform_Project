# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "source" {
    type        = "zip"
    source_dir  = "../src"
    output_path = "/tmp/function.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "zip" {
    source       = data.archive_file.source.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "src-${data.archive_file.source.output_md5}.zip"
    bucket       = google_storage_bucket.function_bucket.name

    # Dependencies are automatically inferred so these lines can be deleted
    depends_on   = [
        google_storage_bucket.function_bucket,  # declared in `storage.tf`
        data.archive_file.source
    ]
}

# Create the Cloud function triggered by a `Finalize` event on the bucket
resource "google_cloudfunctions_function" "function"{
    name                  = "function-trigger-on-gcs"
    runtime               = "python37"  # of course changeable

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.zip.name

    # Must match the function name in the cloud function `main.py` source code
    entry_point           = "cloud_function"
    
    # 
    event_trigger {
        event_type = "google.storage.object.finalize"
        resource   = "${var.project_id}-input"
    }

    # Dependencies are automatically inferred so these lines can be deleted
    depends_on            = [
        google_storage_bucket.function_bucket,  # declared in `storage.tf`
        google_storage_bucket_object.zip
    ]
}

# create pub/sub topic
resource "google_pubsub_topic" "topic" {
  name = "terraform-topic"
}

# create a schedular (cron job) for every minute
resource "google_cloud_scheduler_job" "job" {
  name        = "terraform-job"
  description = "test job triggers cloud function every 10 minutes"
  schedule    = "*/10 * * * *"

  pubsub_target {
      # topic.id is the topic's full resource name.
     topic_name = "${google_pubsub_topic.topic.id}"  # interpolation referencing
      data       = base64encode("testing")
    }
}

# create function
resource "google_cloudfunctions_function" "pubsub_function" {
  name        = "gcs-bigquery"
  description = "move files from gcs and overwrite to BQ every 1 hour"
  runtime     = "python37"

  #available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = google_storage_bucket_object.zip.name
#   source_archive_bucket = "${google_storage_bucket.my-bucket.name}"   # interpolation referencing
#   source_archive_object = "${google_storage_bucket_object.archive.name}"   # interpolation referencing
  entry_point           = "hello_pubsub"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource = "${google_pubsub_topic.topic.name}"  # interpolation referencing
  }
}