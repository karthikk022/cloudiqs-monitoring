terraform {
  backend "s3" {
    bucket = "cloudiqs-terraform-state"
    key    = "environments/monitoring/terraform.tfstate"
    region = "ap-south-1"
  }
}

module "monitoring" {
  source = "../../modules/monitoring-account"

  aws_region         = "ap-south-1"
  account_id         = "000000000001"
  member_account_ids = ["000000000002", "000000000003", "000000000004", "000000000005"]
  environment        = "production"
}
