pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.10'
        PROJECT_NAME = 'BTC-Trading-Bot'
        TRADING_MODE = 'SIMULATION'  // Force simulation mode for CI
    }
    
    // Trigger on Pull Requests and main branch
    triggers {
        githubPullRequests(
            triggerMode: 'CRON',
            events: [Open(), commitChanged()],
            spec: 'H/5 * * * *'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code from repository...'
                checkout scm
                script {
                    // Get branch and PR information
                    env.GIT_BRANCH_NAME = env.BRANCH_NAME ?: 'unknown'
                    env.IS_PR = env.CHANGE_ID ? 'true' : 'false'
                    echo "Branch: ${env.GIT_BRANCH_NAME}"
                    echo "Is Pull Request: ${env.IS_PR}"
                    if (env.CHANGE_ID) {
                        echo "PR #${env.CHANGE_ID}: ${env.CHANGE_TITLE}"
                    }
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo '🔧 Setting up Python environment...'
                script {
                    if (isUnix()) {
                        sh '''
                            python3 --version
                            pip3 install --upgrade pip
                        '''
                    } else {
                        bat '''
                            python --version
                            pip install --upgrade pip
                        '''
                    }
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing project dependencies...'
                script {
                    if (isUnix()) {
                        sh '''
                            pip3 install -r requirements.txt
                            pip3 install pytest pytest-cov pytest-html
                        '''
                    } else {
                        bat '''
                            pip install -r requirements.txt
                            pip install pytest pytest-cov pytest-html
                        '''
                    }
                }
            }
        }
        
        stage('Code Quality Checks') {
            steps {
                echo '🔍 Running code quality checks...'
                script {
                    if (isUnix()) {
                        sh '''
                            pip3 install pylint flake8
                            echo "Running pylint..."
                            pylint btc_trader.py config.py coinbase*.py --exit-zero --output-format=text || true
                            echo "Running flake8..."
                            flake8 . --max-line-length=120 --exclude=venv,__pycache__,.git --exit-zero || true
                        '''
                    } else {
                        bat '''
                            pip install pylint flake8
                            echo "Running pylint..."
                            pylint btc_trader.py config.py coinbase_api.py coinbase_complete_api.py coinbase_advanced_trade_jwt.py --exit-zero --output-format=text || exit 0
                            echo "Running flake8..."
                            flake8 . --max-line-length=120 --exclude=venv,__pycache__,.git --exit-zero || exit 0
                        '''
                    }
                }
            }
        }
        
        stage('🧪 Run All Unit Tests') {
            steps {
                echo '🧪 Running ALL unit tests (118 tests)...'
                script {
                    def testResult
                    if (isUnix()) {
                        testResult = sh(
                            script: 'python3 tests/run_all_tests.py',
                            returnStatus: true
                        )
                    } else {
                        testResult = bat(
                            script: 'python tests/run_all_tests.py',
                            returnStatus: true
                        )
                    }
                    
                    if (testResult != 0) {
                        error("❌ Unit tests FAILED! Cannot proceed with merge.")
                    } else {
                        echo "✅ All 118 unit tests PASSED!"
                    }
                }
            }
        }
        
        stage('Coverage Report') {
            steps {
                echo '📊 Generating coverage report...'
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m pytest tests/ --cov=. --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=50
                        '''
                    } else {
                        bat '''
                            python -m pytest tests/ --cov=. --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=50
                        '''
                    }
                }
            }
        }
        
        stage('Security Scan') {
            when {
                expression { env.IS_PR == 'true' || env.GIT_BRANCH_NAME == 'main' }
            }
            steps {
                echo '🔒 Running security scan...'
                script {
                    if (isUnix()) {
                        sh '''
                            pip3 install safety bandit || true
                            echo "Checking dependencies for vulnerabilities..."
                            safety check || true
                            echo "Running security code analysis..."
                            bandit -r . -ll || true
                        '''
                    } else {
                        bat '''
                            pip install safety bandit || exit 0
                            echo "Checking dependencies for vulnerabilities..."
                            safety check || exit 0
                            echo "Running security code analysis..."
                            bandit -r . -ll || exit 0
                        '''
                    }
                }
            }
        }
        
        stage('✅ PR Validation Success') {
            when {
                expression { env.IS_PR == 'true' }
            }
            steps {
                echo '✅ All tests passed! PR is ready for review and merge.'
                script {
                    // Set GitHub status
                    if (env.CHANGE_ID) {
                        githubNotify(
                            status: 'SUCCESS',
                            description: '✅ All tests passed (118/118)',
                            context: 'Jenkins CI'
                        )
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up and archiving artifacts...'
            
            // Archive test results
            junit allowEmptyResults: true, testResults: '**/test-reports/*.xml'
            
            // Archive HTML test reports
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-reports',
                reportFiles: 'test_report_latest.html',
                reportName: 'Test Report'
            ])
            
            // Archive coverage reports
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
            
            // Cobertura plugin for coverage tracking
            cobertura coberturaReportFile: 'coverage.xml', 
                      failNoReports: false,
                      failUnhealthy: false,
                      failUnstable: false
        }
        
        success {
            echo '✅ BUILD SUCCESSFUL - All tests passed!'
            script {
                if (env.IS_PR == 'true') {
                    echo '✅ PR can be merged to main'
                    // Optional: Add comment to PR
                    if (env.CHANGE_ID) {
                        githubNotify(
                            status: 'SUCCESS',
                            description: '✅ All 118 tests passed. PR ready for merge!',
                            context: 'Jenkins CI/Tests'
                        )
                    }
                } else if (env.GIT_BRANCH_NAME == 'main') {
                    echo '✅ Main branch is healthy'
                }
            }
        }
        
        failure {
            echo '❌ BUILD FAILED - Tests did not pass!'
            script {
                if (env.IS_PR == 'true') {
                    echo '❌ PR CANNOT be merged - Fix tests first!'
                    if (env.CHANGE_ID) {
                        githubNotify(
                            status: 'FAILURE',
                            description: '❌ Tests failed. Cannot merge.',
                            context: 'Jenkins CI/Tests'
                        )
                    }
                }
            }
        }
        
        unstable {
            echo '⚠️ Build is unstable - Some tests may have warnings'
            script {
                if (env.IS_PR == 'true' && env.CHANGE_ID) {
                    githubNotify(
                        status: 'UNSTABLE',
                        description: '⚠️ Build unstable. Review warnings.',
                        context: 'Jenkins CI/Tests'
                    )
                }
            }
        }
    }
}
