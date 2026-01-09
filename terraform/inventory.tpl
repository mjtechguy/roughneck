[roughneck]
${server_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${private_key_path}

[roughneck:vars]
enable_gastown=${enable_gastown}
enable_beads=${enable_beads}
enable_k9s=${enable_k9s}
enable_systemd_services=${enable_systemd_services}
enable_letsencrypt=${enable_letsencrypt}
domain_name=${domain_name}
