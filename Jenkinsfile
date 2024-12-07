pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'network-congestion-prediction'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = 'docker.io'
        GMAIL_USER = 'nouhailangr275128@gmail.com'
        GMAIL_PASSWORD = 'elhf fkrg xrfb mknn'
        SONAR_SCANNER_HOME = tool (name: 'SonarQube Scanner') // Use the tool name you configured in Jenkins
    }

    stages {
        stage('Setup Environment') {
            steps {
                // Install Node.js
                sh '''
                curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
                apt-get install -y nodejs
                '''
            }
        }
        
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Nouhailangr/network-congestion-prediction'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_IMAGE:$DOCKER_TAG .'
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

stage('Code Quality Analysis') {
    steps {
        script {
            withSonarQubeEnv('SonarQube') { // 'SonarQube' is the name you gave the SonarQube server in Jenkins
                sh '''
                    $SONAR_SCANNER_HOME/bin/sonar-scanner \
                    -Dsonar.projectKey=network-congestion-prediction \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://host.docker.internal:9000  # Adjust if using a remote server
                    -Dsonar.login=SonarQube-Token
                '''
            }
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
                script {
                    archiveArtifacts artifacts: 'test_results.txt', allowEmptyArchive: true
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
