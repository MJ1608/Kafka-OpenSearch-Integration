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
        stage('Check Services') {
            steps {
                sh 'docker-compose ps'
            }
        }
        stage('Test') {
            steps {
                // Test the Kafka services
                sh 'docker-compose exec kafka1 pytest tests/'
                sh 'docker-compose exec kafka2 pytest tests/'
                sh 'docker-compose exec kafka3 pytest tests/'
                
                // Test the OpenSearch services
                sh 'docker-compose exec opensearch pytest tests/'
                sh 'docker-compose exec opensearch-dashboards pytest tests/'
                
                // Test the Zookeeper service (if you have tests for Zookeeper)
                // sh 'docker-compose exec zookeeper pytest tests/'
            }
        }
    }

    post {
        always {
            sh 'docker-compose down'
        }
    }
}
