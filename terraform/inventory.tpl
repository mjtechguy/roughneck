[roughneck]
${server_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${private_key_path}

[roughneck:vars]
enable_gastown=${enable_gastown}
enable_beads=${enable_beads}
enable_k9s=${enable_k9s}
enable_systemd_services=${enable_systemd_services}
enable_autocoder=${enable_autocoder}
enable_glm=${enable_glm}
zai_key=${zai_key}
enable_letsencrypt=${enable_letsencrypt}
domain_name=${domain_name}
tls_mode=${tls_mode}
dns_provider=${dns_provider}
cloudflare_api_token=${cloudflare_api_token}
route53_access_key=${route53_access_key}
route53_secret_key=${route53_secret_key}
digitalocean_dns_token=${digitalocean_dns_token}
hetzner_dns_token=${hetzner_dns_token}
