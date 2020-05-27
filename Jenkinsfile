properties([pipelineTriggers([githubPush()])])

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'echo "Building environment ... "'
                ansiblePlaybook become: true, colorized: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'build_env.yaml', vaultCredentialsId: 'vault_cred', disableHostKeyChecking: true
            }
        }
        stage('Test modules') {
            steps {
                ansiblePlaybook become: true, colorized: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'mysql.yaml', vaultCredentialsId: 'vault_cred', disableHostKeyChecking: true
            }
        }
    }
}