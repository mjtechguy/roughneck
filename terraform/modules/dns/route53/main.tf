# Route 53 DNS module
# Auto-provisions DNS A records for roughneck services
# Provider must be configured in the calling module

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# Look up the hosted zone from the domain name
data "aws_route53_zone" "domain" {
  name = "${var.domain_name}."
}

# code-server subdomain
resource "aws_route53_record" "code" {
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = "code.${var.domain_name}"
  type    = "A"
  ttl     = 300
  records = [var.server_ip]
}

# AutoCoder subdomain (conditional)
resource "aws_route53_record" "autocoder" {
  count   = var.enable_autocoder ? 1 : 0
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = "autocoder.${var.domain_name}"
  type    = "A"
  ttl     = 300
  records = [var.server_ip]
}

# Wildcard record for DNS-01 mode
resource "aws_route53_record" "wildcard" {
  count   = var.tls_mode == "dns01" ? 1 : 0
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = "*.${var.domain_name}"
  type    = "A"
  ttl     = 300
  records = [var.server_ip]
}

# Root domain
resource "aws_route53_record" "root" {
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [var.server_ip]
}
