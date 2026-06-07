terraform {
  backend "s3" {
    bucket = "cloudiqs-terraform-state"
    key    = "environments/customer-a/terraform.tfstate"
    region = "ap-south-1"
  }
}

provider "aws" {
  region = "ap-south-1"
}

module "customer_a" {
  source = "../../modules/member-account"

  aws_region            = "ap-south-1"
  account_id            = "000000000002"
  monitoring_account_id = "000000000001"
  customer_name         = "customer-a"
  environment           = "production"
}
