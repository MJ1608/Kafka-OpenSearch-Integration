pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                // Clone the repository
                git branch: 'main', url: 'https://github.com/MJ1608/Kafka-OpenSearch-Integration.git'
            }
        }

        stage('Build and Deploy') {
            steps {
                // Build the project (if needed)
                sh 'pip install -r requirements.txt'

                // Start Docker services
                sh 'docker-compose up -d'

                // Wait for services to initialize (adjust time based on your project's startup time)
                script {
                    sleep 300  // Wait for 5 minutes (adjust as necessary)
                }
            }
        }


        stage('Run Producer') {
            steps {
                // Run the Python producer script
                sh 'python3 producer.py'

                // Check if Kafka topic is created (example check)
                script {
                    def topicCreated = sh(script: "docker exec -i kafka1 kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -Fx 'wiki'", returnStatus: true)
                    if (topicCreated == 0) {
                        echo 'Kafka topic "wiki" is created.'
                    } else {
                        error 'Failed to create Kafka topic "wiki".'
                    }
                }

                // Wait a bit for data to start being produced (adjust based on expected startup time)
                script {
                    sleep 10  // Wait for 1 minute (adjust as necessary)
                }
            }
        }

        stage('Run Consumer') {
            steps {
                // Run the Python consumer script
                sh 'python3 consumer.py'
            }

            post {
                success {
                    // Verify OpenSearch index existence and state
                    script {
                        try {
                            def response = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:9200/wikimedia", returnStdout: true)
                            if (response.trim() == "200") {
                                echo 'OpenSearch index "wikimedia" is created and accessible.'
                            } else {
                                error 'Failed to verify OpenSearch index "wikimedia".'
                            }
                        } catch (Exception e) {
                            error "Failed to execute HTTP request: ${e.message}"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up resources (e.g., stop Docker containers)
            sh 'docker-compose down'
        }
    }
}
