pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'network-congestion-prediction'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = '515966501608.dkr.ecr.eu-north-1.amazonaws.com'
        ECR_REPO = 'network-congestion-prediction'
        AWS_REGION = 'eu-north-1'
        GMAIL_USER = 'nouhailangr275128@gmail.com'
        GMAIL_PASSWORD = 'elhf fkrg xrfb mknn'
        AWS_ACCESS_KEY_ID = 'AKIAXQIQAALUEHVEZHPM'
        AWS_SECRET_ACCESS_KEY = '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'
        AWS_DEFAULT_REGION = 'eu-north-1'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Nouhailangr/network-congestion-prediction'
            }
        }

        stage('Docker Login') {
            steps {
                script {
                    sh 'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $DOCKER_REGISTRY'
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
                    sh 'docker run --rm $DOCKER_IMAGE:$DOCKER_TAG pylint /app --output-format=text > pylint_report.txt || true'
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
                    sh 'docker run --rm -e PYTHONPATH=/app $DOCKER_IMAGE:$DOCKER_TAG pytest tests/ --maxfail=1 --disable-warnings -q > test_results.txt || true'
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
                    sh 'aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $DOCKER_REGISTRY'
                }
            }
        }

        stage('Tag Docker Image') {
            steps {
                script {
                    sh 'docker tag $DOCKER_IMAGE:$DOCKER_TAG $DOCKER_REGISTRY/$ECR_REPO:$DOCKER_TAG'
                }
            }
        }

        stage('Push Docker Image to AWS ECR') {
            steps {
                sh 'docker push $DOCKER_REGISTRY/$ECR_REPO:$DOCKER_TAG'
            }
        }
    }

    post {

        success {
            mail to: "$GMAIL_USER",
                 subject: "Jenkins Build Success - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "The build for ${env.JOB_NAME} #${env.BUILD_NUMBER} was successful. Check the build logs for more details.\n\nBuild URL: ${env.BUILD_URL}",
                 from: "$GMAIL_USER",
                 mimeType: 'text/plain'
        }

        failure {
            mail to: "$GMAIL_USER",
                 subject: "Jenkins Build Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "The build for ${env.JOB_NAME} #${env.BUILD_NUMBER} has failed. Please check the build logs for errors.\n\nBuild URL: ${env.BUILD_URL}",
                 from: "$GMAIL_USER",
                 mimeType: 'text/plain'
        }
    }
}
