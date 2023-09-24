pipeline {
    agent any

    triggers {
        cron('H H * * 2,3') // Runs on Tuesdays and Wednesdays
    }

    stages {
        stage('Check If Odd Week') {
            steps {
                script {
                    def calendar = Calendar.getInstance()
                    def weekOfYear = calendar.get(Calendar.WEEK_OF_YEAR)
                    if (weekOfYear % 2 == 0) {
                        echo "Today is in an odd week of the year. Proceeding with the build."
                    } else {
                        echo "Today is not in an odd week of the year. Skipping the build."
                        currentBuild.result = 'ABORTED'
                        error("Build aborted in even weeks.")
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
