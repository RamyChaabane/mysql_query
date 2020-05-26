pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                ansiblePlaybook become: true, colorized: true, inventory: 'inventory', playbook: 'install_pkg.yaml', vaultCredentialsId: 'vault_cred'
            }
        }
    }
}
