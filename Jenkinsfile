properties([pipelineTriggers([githubPush()])])

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                ansiblePlaybook
                    become: true,
                    credentialsId: 'ansible_login',
                    inventory: 'inventory',
                    playbook: 'build_env.yaml',
                    vaultCredentialsId: 'vault_cred',
                    disableHostKeyChecking: true
            }
        }
        stage('Test modules') {
            steps {
                ansiblePlaybook
                    become: true,
                    credentialsId: 'ansible_login',
                    inventory: 'inventory',
                    playbook: 'mysql.yaml',
                    vaultCredentialsId: 'vault_cred',
                    disableHostKeyChecking: true
            }
        }
        stage('Publish to Production') {
            steps{
                input "is module working as expected?"
                sshPublisher(
                    publishers: [
                        sshPublisherDesc(
                            configName: 'prod_server',
                            transfers: [
                                sshTransfer(
                                    cleanRemote: false,
                                    excludes: '',
                                    execCommand: '',
                                    execTimeout: 120000,
                                    flatten: false,
                                    makeEmptyDirs: false,
                                    noDefaultExcludes: false,
                                    patternSeparator: '[, ]+',
                                    remoteDirectory: '',
                                    remoteDirectorySDF: false,
                                    removePrefix: '',
                                    sourceFiles: 'library/mysql_query.py'
                                )
                            ],
                            usePromotionTimestamp: false,
                            useWorkspaceInPromotion: false,
                            verbose: false
                        )
                    ]
                )
            }
        }
    }
}
