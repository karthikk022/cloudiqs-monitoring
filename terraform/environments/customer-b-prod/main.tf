terraform {
  backend "s3" {
    bucket = "cloudiqs-terraform-state"
    key    = "environments/customer-b-prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "customer_b_prod" {
  source = "../../modules/member-account"

  aws_region            = "us-east-1"
  account_id            = "000000000003"
  monitoring_account_id = "000000000001"
  customer_name         = "customer-b-prod"
  environment           = "production"
}
