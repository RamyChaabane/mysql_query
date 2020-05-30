properties([pipelineTriggers([githubPush()])])

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                ansiblePlaybook become: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'build_env.yaml', vaultCredentialsId: 'vault_cred', disableHostKeyChecking: true
            }
        }
        stage('Test modules') {
            steps {
                ansiblePlaybook become: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'mysql.yaml', vaultCredentialsId: 'vault_cred', disableHostKeyChecking: true
            }
        }
        stage('Publish to Production') {
            steps{
                input "is module working as expected?"
                withCredentials([sshUserPrivateKey(credentialsId: 'ansible_login', keyFileVariable: 'ansible_priv_key', passphraseVariable: '', usernameVariable: 'login_user')])  {
                    sshPublisher(
                        publishers: [
                            sshPublisherDesc(
                                configName: 'prod_server',
                                sshCredentials: [
                                    keyPath: '$ansible_priv_key',
                                    username: '$login_user'
                                ],
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
                                        remoteDirectory: '/home/cloud_user/',
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: 'library'
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
}
