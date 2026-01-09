[roughneck]
${server_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${private_key_path}

[roughneck:vars]
git_user_name=${git_user_name}
git_user_email=${git_user_email}
enable_gastown=${enable_gastown}
enable_beads=${enable_beads}
enable_k9s=${enable_k9s}
enable_systemd_services=${enable_systemd_services}
