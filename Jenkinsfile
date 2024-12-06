pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'network-congestion-prediction'
        DOCKER_TAG = 'latest'
        DOCKER_REGISTRY = 'docker.io' // Adjust if needed
        GMAIL_USER = 'nouhailangr275128@gmail.com'  // Replace with your Gmail address
        GMAIL_PASSWORD = 'elhf fkrg xrfb mknn'  // Replace with your generated app password
        TEST_RESULTS_DIR = '"$WORKSPACE/Network Congestion/test-results"' // Directory for test results with quotes
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

        stage('Run Tests') {
            steps {
                script {
                    // Ensure the test results directory exists
                    sh "mkdir -p $TEST_RESULTS_DIR"
                    
                    // Run the tests using pytest and save the output to an XML file
                    sh "docker run --rm -v $TEST_RESULTS_DIR:/app/test-results -e PYTHONPATH=/app $DOCKER_IMAGE:$DOCKER_TAG pytest tests/ --maxfail=1 --disable-warnings -q --junitxml=/app/test-results/test-results.xml" 
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
