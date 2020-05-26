properties([pipelineTriggers([githubPush()])])

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'whoami'
                ansiblePlaybook become: true, colorized: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'install_pkg.yaml', vaultCredentialsId: 'vault_cred', disableHostKeyChecking: true
            }
        }
    }
}
