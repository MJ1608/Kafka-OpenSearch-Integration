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
                sh '/home/mj/.local/bin/flake8 producer.py consumer.py'
                
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker-compose up -d'  
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
