  
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.52.0"
      credentials = file("creds.json")
    }
  }

  required_version = "~> 0.14"
}