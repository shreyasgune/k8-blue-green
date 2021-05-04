  
provider google {
    source  = "hashicorp/google"
    version = "3.52.0"
    credentials = file("creds.json")
  }