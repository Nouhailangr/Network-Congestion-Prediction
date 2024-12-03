pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'network-congestion-prediction'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = 'docker.io' // Adjust if needed
        SONARQUBE_SCANNER = tool name: 'SonarQubeScanner', type: 'SonarQubeScanner'
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

        stage('Run SonarQube Analysis') {
            steps {
                script {
                    // Run SonarQube analysis inside Docker container
                    sh '''
                        docker run --rm \
                            -e SONARQUBE_URL=http://localhost:9000 \
                            -e SONARQUBE_TOKEN=$SONARQUBE_TOKEN \
                            -v $(pwd):/usr/src/app \
                            $DOCKER_IMAGE:$DOCKER_TAG \
                            $SONARQUBE_SCANNER -Dsonar.projectKey=network-congestion-prediction \
                            -Dsonar.sources=src \
                            -Dsonar.host.url=$SONARQUBE_URL
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run the tests using pytest
                    sh 'docker run --rm -e PYTHONPATH=/app $DOCKER_IMAGE:$DOCKER_TAG pytest tests/ --maxfail=1 --disable-warnings -q'  // Assuming tests are in the 'tests' folder
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
                    sh 'docker rmi -f network-ongestion-prediction:latest || true'
                }
            }
        }
    }

    post {
        always {
            // Optionally clean up Docker images
            sh 'docker rmi $DOCKER_IMAGE:$DOCKER_TAG || true'
        }
    }
}
