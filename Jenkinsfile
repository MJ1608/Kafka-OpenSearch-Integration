pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/MJ1608/Kafka-OpenSearch-Integration.git'
            }
        }


        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Linting') {
            steps {
                sh 'pip install flake8 pylint'  // Install linting tools
                sh 'flake8 producer.py consumer.py'  // Check style violations
                sh 'pylint producer.py consumer.py'  // Check for code quality issues
            }
        }

        stage('Deploy') {
            steps {
                // Example deployment steps (e.g., Docker build/push, Kubernetes apply)
                sh 'docker-compose up -d'  // Deploy using Docker Compose
            }
        }

        stage('Check Services') {
            steps {
                sh 'docker-compose ps'
            }
        }

    }

    post {
        always {
            sh 'docker-compose down'
        }
    }
}
