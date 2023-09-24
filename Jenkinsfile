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
                // Your test steps go here
            }
        }
        stage('Deploy') {
            steps {
                // Your deployment steps go here
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
