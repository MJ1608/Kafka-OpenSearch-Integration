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
                sh 'pip install flake8'  // Install linting tools
                sh '/home/mj/.local/bin/flake8 producer.py consumer.py'
                
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
