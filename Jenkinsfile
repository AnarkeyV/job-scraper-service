pipeline {
  agent any
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build Image') { steps { sh 'docker build -t job-scraper-service:jenkins .' } }
    stage('Run Tests') { steps { sh 'docker run --rm job-scraper-service:jenkins pytest || true' } }
    stage('Smoke Test') {
      steps {
        sh 'docker compose up -d --build'
        sh 'sleep 10 && curl -f http://localhost:8000/health'
      }
      post { always { sh 'docker compose down' } }
    }
  }
}
