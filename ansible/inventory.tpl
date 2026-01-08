[roughneck]
${server_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${private_key_path}

[roughneck:vars]
git_user_name=${git_user_name}
git_user_email=${git_user_email}
roughneck_repo=${roughneck_repo}
roughneck_branch=${roughneck_branch}
anthropic_api_key=${anthropic_api_key}
enable_systemd_services=${enable_systemd_services}
