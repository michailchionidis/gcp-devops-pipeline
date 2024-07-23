# Create a Google Cloud Storage bucket
resource "google_storage_bucket" "bucket" {
  name     = "dataprojects-io-my-terraform-bucket"
  location = "EU"
}

output "bucket_url" {
  value = google_storage_bucket.bucket.url
}
