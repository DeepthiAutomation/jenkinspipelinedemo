pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                // Your build steps go here
                sh 'echo "Hello, Jenkins!"'
            }
        }
        stage('Test') {
            steps {
                sh 'echo "Hello, Jenkins!"'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo "Hello, Jenkins!"'
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
