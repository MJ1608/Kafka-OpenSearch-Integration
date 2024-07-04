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
                sh 'docker-compose up -d --build'
            }
        }
        stage('Test') {
            steps {
                sh 'docker-compose exec service_name pytest tests/'
            }
        }
    }

    post {
        always {
            sh 'docker-compose down'
        }
    }
}
