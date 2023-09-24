pipeline {
    agent any

    triggers {
        cron('H H * * 2') // Runs every Tuesday
    }

    stages {
        stage('Check If Alternate Tuesday') {
            steps {
                script {
                    def calendar = Calendar.getInstance()
                    def dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK)
                    if (dayOfWeek == Calendar.TUESDAY || dayOfWeek == Calendar.SUNDAY) {
                        echo "Today is an alternate Tuesday. Proceeding with the build."
                    } else {
                        echo "Today is not an alternate Tuesday. Skipping the build."
                        currentBuild.result = 'ABORTED'
                        error("Build aborted on non-alternate Tuesday.")
                    }
                }
            }
        }

        stage('Build') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('ABORTED') }
            }
            steps {
                // Your build steps go here
                sh 'echo "Hello, Jenkins!"'
            }
        }
        // Add more stages as needed
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
