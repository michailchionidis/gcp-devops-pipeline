# Create a BigQuery dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = "my_terraform_dataset"
  location   = "EU"
}

output "dataset_id" {
  value = google_bigquery_dataset.dataset.dataset_id
}