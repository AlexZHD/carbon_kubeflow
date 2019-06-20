# domain name to beusing in cluster
variable "name" {
  default = "zdevops.xyz"
}

variable "region" {
  default = "us-west-2"
}

# aws ec2 describe-availability-zones --region us-west-2
# us-west-2a, us-west-2b, us-west-2c, us-west-2d
variable "azs" {
  default = ["us-west-2a", "us-west-2b", "us-west-2c"]
  # default = ["us-west-2a", "us-west-2b"]
  type    = "list"
}

variable "env" {
  default = "staging"
}

variable "vpc_cidr" {
  default = "10.20.0.0/16"
  # default = "10.0.0.0/26"
}
