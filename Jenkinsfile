pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                ansiblePlaybook become: true, colorized: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'setup_ssh_connect.yaml', vaultCredentialsId: 'vault_cred'
            }
        }
    }
}
