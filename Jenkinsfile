pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'whoami'
                ansiblePlaybook become: true, colorized: true, inventory: 'inventory', playbook: 'install_pkg.yaml', vaultCredentialsId: 'vault_cred'
            }
        }
    }
}
