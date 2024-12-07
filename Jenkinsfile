pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'network-congestion-prediction'
        DOCKER_TAG = 'latest'
        AWS_REGION = 'us-east-1'  // Replace with your AWS region
        ECR_REPOSITORY = 'network-congestion-prediction'  // Replace with your ECR repository name
        GMAIL_USER = 'nouhailangr275128@gmail.com'  // Replace with your Gmail address
        GMAIL_PASSWORD = 'elhf fkrg xrfb mknn'  // Replace with your generated app password
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Clone your Git repository containing the Flask app code
                git branch: 'main', url: 'https://github.com/Nouhailangr/network-congestion-prediction' // Replace with your GitHub URL
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t $DOCKER_IMAGE:$DOCKER_TAG .'
                }
            }
        }

        stage('Run Pylint') {
            steps {
                script {
                    // Run pylint inside the container to check code quality
                    sh '''
                        docker run --rm $DOCKER_IMAGE:$DOCKER_TAG pylint /app --output-format=text > pylint_report.txt || true
                    '''
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Run the Docker container
                    sh 'docker run -d -p 9090:5001 $DOCKER_IMAGE:$DOCKER_TAG'
                }
            }
        }

        stage('Install Test Dependencies') {
            steps {
                script {
                    // Install Python dependencies for testing
                    sh 'docker run --rm $DOCKER_IMAGE:$DOCKER_TAG pip install pytest flask'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run the tests using pytest and save the results to a file
                    sh '''
                        docker run --rm -e PYTHONPATH=/app $DOCKER_IMAGE:$DOCKER_TAG pytest tests/ --maxfail=1 --disable-warnings -q > test_results.txt || true
                    '''
                }
            }
        }

        stage('Archive Test Results') {
            steps {
                script {
                    // Archive the test results file as an artifact
                    archiveArtifacts artifacts: 'test_results.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Archive Pylint Report') {
            steps {
                script {
                    // Archive the pylint report as an artifact
                    archiveArtifacts artifacts: 'pylint_report.txt', allowEmptyArchive: true
                }
            }
        }

        // Add stage to authenticate with AWS ECR
        stage('Authenticate with AWS ECR') {
            steps {
                script {
                    // Authenticate Docker with ECR using AWS CLI
                    sh '''
                        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin 515966501608.dkr.ecr.${AWS_REGION}.amazonaws.com
                    '''
                }
            }
        }

        // Add stage to tag Docker image for ECR
        stage('Tag Docker Image for ECR') {
            steps {
                script {
                    sh '''
                        docker tag $DOCKER_IMAGE:$DOCKER_TAG 515966501608.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY:$DOCKER_TAG
                    '''
                }
            }
        }

        // Add stage to push Docker image to ECR
        stage('Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                        docker push 515966501608.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY:$DOCKER_TAG
                    '''
                }
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
            // Optionally clean up Docker images
            sh 'docker rmi $DOCKER_IMAGE:$DOCKER_TAG || true'
        }
        success {
            mail to: 'nouhailangr275128@gmail.com',  // Replace with your recipient's email address
                subject: "Jenkins Build Success - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "The build for ${env.JOB_NAME} #${env.BUILD_NUMBER} was successful. Check the build logs for more details.\n\nBuild URL: ${env.BUILD_URL}",
                from: "$GMAIL_USER",
                mimeType: 'text/plain'
        }

        failure {
            mail to: 'nouhailangr275128@gmail.com',  // Replace with your recipient's email address
                subject: "Jenkins Build Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "The build for ${env.JOB_NAME} #${env.BUILD_NUMBER} has failed. Please check the build logs for errors.\n\nBuild URL: ${env.BUILD_URL}",
                from: "$GMAIL_USER",
                mimeType: 'text/plain'
        }
    }
}
