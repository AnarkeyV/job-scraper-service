terraform {
  required_version = ">= 1.7.0"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
}
provider "google" { project = var.project_id region = var.region }
variable "project_id" {}
variable "region" { default = "asia-southeast1" }
# Weekend MVP note: add Cloud Run or GKE resources only after local Docker version works.
