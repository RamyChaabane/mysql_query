properties([pipelineTriggers([githubPush()])])

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                ansiblePlaybook become: true, credentialsId: 'ansible_login', inventory: 'inventory', playbook: 'build_env.yaml', vaultCredentialsId: 'vault_cred', disableHostKeyChecking: true
                archiveArtifacts artifacts: 'library.zip', onlyIfSuccessful: true
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
                milestone[1]
                withCredentials([usernamePassword(credentialsId: 'prod_cred', passwordVariable: 'password_login', usernameVariable: 'user_login')]) {
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
                                        remoteDirectory: '/home/cloud_user/',
                                        remoteDirectorySDF: false,
                                        removePrefix: '',
                                        sourceFiles: 'library.zip'
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
