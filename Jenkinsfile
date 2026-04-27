pipeline {
    agent any

    environment {
        // Ensure Jenkins can find npm (typically in /usr/local/bin or /opt/homebrew/bin)
        PATH = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
    }

    triggers {
        // Checks GitHub every minute for new pushes and automatically triggers the build
        pollSCM('* * * * *')
    }

    stages {
        stage('Checkout Source') {
            steps {
                // Checkout the code from your GitHub repository
                checkout scm
            }
        }

        stage('Setup Backend (Python)') {
            steps {
                echo 'Installing Python Dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Validate Backend') {
            steps {
                echo 'Compiling Python scripts to check for syntax errors...'
                sh '''
                    . venv/bin/activate
                    python3 -m py_compile api.py model.py generate_data.py
                '''
            }
        }

        stage('Setup Frontend (Node.js)') {
            steps {
                echo 'Installing Node Dependencies...'
                dir('telecom-dashboard') {
                    sh 'npm install'
                }
            }
        }

        stage('Build Frontend (React/Vite)') {
            steps {
                echo 'Building production bundle...'
                dir('telecom-dashboard') {
                    sh 'npm run build'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo '✅ Build Successful! The Telecom Dashboard is ready for deployment.'
            // Here you could add steps to SCP the build artifacts or restart the server
        }
        failure {
            echo '❌ Build Failed. Please check the logs.'
        }
    }
}
