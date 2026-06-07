terraform {
  backend "s3" {
    bucket = "cloudiqs-terraform-state"
    key    = "environments/customer-c/terraform.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  region = "eu-west-1"
}

module "customer_c" {
  source = "../../modules/member-account"

  aws_region            = "eu-west-1"
  account_id            = "000000000005"
  monitoring_account_id = "000000000001"
  customer_name         = "customer-c"
  environment           = "production"
}
