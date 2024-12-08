pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'network-congestion-prediction'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = '515966501608.dkr.ecr.eu-north-1.amazonaws.com' // Your ECR registry URL
        ECR_REPO = 'network-congestion-prediction' // ECR repository name
        AWS_REGION = 'eu-north-1' // AWS region
        GMAIL_USER = 'nouhailangr275128@gmail.com'  // Replace with your Gmail address
        GMAIL_PASSWORD = 'elhf fkrg xrfb mknn'  // Replace with your generated app password
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Nouhailangr/network-congestion-prediction' // Replace with your GitHub URL
            }
        }

        stage('Docker Login') {
            steps {
                script {
                    sh '''
                    aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 515966501608.dkr.ecr.eu-north-1.amazonaws.com
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_IMAGE:$DOCKER_TAG .'
                }
            }
        }

        stage('Run Pylint') {
            steps {
                script {
                    sh '''
                        docker run --rm $DOCKER_IMAGE:$DOCKER_TAG pylint /app --output-format=text > pylint_report.txt || true
                    '''
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    sh 'docker run -d -p 9090:5001 $DOCKER_IMAGE:$DOCKER_TAG'
                }
            }
        }

        stage('Install Test Dependencies') {
            steps {
                script {
                    sh 'docker run --rm $DOCKER_IMAGE:$DOCKER_TAG pip install pytest flask'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                        docker run --rm -e PYTHONPATH=/app $DOCKER_IMAGE:$DOCKER_TAG pytest tests/ --maxfail=1 --disable-warnings -q > test_results.txt || true
                    '''
                }
            }
        }

        stage('Archive Test Results') {
            steps {
                archiveArtifacts artifacts: 'test_results.txt', allowEmptyArchive: true
            }
        }

        stage('Archive Pylint Report') {
            steps {
                archiveArtifacts artifacts: 'pylint_report.txt', allowEmptyArchive: true
            }
        }

                stage('Authenticate AWS ECR') {
            steps {
                script {
                    // Authenticate Docker to AWS ECR
                    sh '''
                        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $DOCKER_REGISTRY
                    '''
                }
            }
        }

        stage('Tag Docker Image') {
            steps {
                script {
                    // Tag the Docker image with the ECR repository URL
                    sh 'docker tag $DOCKER_IMAGE:$DOCKER_TAG $DOCKER_REGISTRY/$ECR_REPO:$DOCKER_TAG'
                }
            }
        }

        stage('Push Docker Image to AWS ECR') {
            steps {
                sh 'docker push 515966501608.dkr.ecr.eu-north-1.amazonaws.com/network-congestion-prediction:latest'
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    def containerId = sh(script: "docker ps -q --filter name=network-congestion-prediction", returnStdout: true).trim()
                    if (containerId) {
                        sh "docker stop ${containerId}"
                        sh "docker rm ${containerId}"
                    } else {
                        echo "No running containers to clean up."
                    }
                    sh 'docker rmi -f network-congestion-prediction:latest || true'
                }
            }
        }
    }

    post {
        always {
            sh 'docker rmi $DOCKER_IMAGE:$DOCKER_TAG || true'
        }
        success {
            mail to: 'nouhailangr275128@gmail.com',  
                subject: "Jenkins Build Success - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "The build for ${env.JOB_NAME} #${env.BUILD_NUMBER} was successful. Check the build logs for more details.\n\nBuild URL: ${env.BUILD_URL}",
                from: "$GMAIL_USER",
                mimeType: 'text/plain'
        }

        failure {
            mail to: 'nouhailangr275128@gmail.com',  
                subject: "Jenkins Build Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "The build for ${env.JOB_NAME} #${env.BUILD_NUMBER} has failed. Please check the build logs for errors.\n\nBuild URL: ${env.BUILD_URL}",
                from: "$GMAIL_USER",
                mimeType: 'text/plain'
        }
    }
}
