[gastown]
${server_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${private_key_path}

[gastown:vars]
git_user_name=${git_user_name}
git_user_email=${git_user_email}
gastown_repo=${gastown_repo}
gastown_branch=${gastown_branch}
anthropic_api_key=${anthropic_api_key}
enable_systemd_services=${enable_systemd_services}
