pipeline {
    agent any

    environment {
        IMAGE_NAME = 'job-scraper-service'
        IMAGE_TAG = 'jenkins'
        CONTAINER_NAME = 'job-scraper-service-jenkins-test'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest'
            }
        }

        stage('Smoke Test Container') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      -p 8001:8000 \
                      ${IMAGE_NAME}:${IMAGE_TAG}

                    sleep 8

                    curl -f http://localhost:8001/health
                '''
            }
            post {
                always {
                    sh 'docker rm -f ${CONTAINER_NAME} || true'
                }
            }
        }
    }

    post {
        success {
            echo 'Jenkins pipeline completed successfully.'
        }

        failure {
            echo 'Jenkins pipeline failed. Check the failed stage above.'
        }

        always {
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
    }
}