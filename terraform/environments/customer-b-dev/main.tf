terraform {
  backend "s3" {
    bucket = "cloudiqs-terraform-state"
    key    = "environments/customer-b-dev/terraform.tfstate"
    region = "ap-south-1"
  }
}

provider "aws" {
  region = "ap-south-1"
}

module "customer_b_dev" {
  source = "../../modules/member-account"

  aws_region            = "ap-south-1"
  account_id            = "000000000004"
  monitoring_account_id = "000000000001"
  customer_name         = "customer-b-dev"
  environment           = "development"
}
