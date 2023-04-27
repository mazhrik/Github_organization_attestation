pipeline {
    agent {
        node {
        // your node configuration here
        }
    }

    stages {
        stage('Checkout') {
            steps {
                checkout()
            }
        }
        stage('Running Script And Installing Dependencies') {
            steps {
                script {
                    bat """
                    pip install -r requirements.txt
                    set Token=${params.Token}
                    python auto.py
                    """
                }
                script {
                    def currentDate = new Date()
                    def currentMonth = currentDate.getMonth() + 1 // Note: months are 0-based in JavaScript
                    def currentYear = currentDate.getYear() + 1900 // Note: years are represented as years since 1900 in JavaScript
                    def quater, year
                    if (currentMonth >= 1 && currentMonth <= 3) {
                        quater = "Q1"
                        year = currentYear
                    } else if (currentMonth >= 4 && currentMonth <= 8) {
                        quater = "Q2"
                        year = currentYear
                    } else {
                        quater = "Q3"
                        year = currentYear - 1
                    }
                    def server = Artifactory.server 'EnterpriseArtifactory'
                    def timestamp = new Date(currentBuild.startTimeInMillis).format("yyyy-MM-dd-HH-mm-ss")
                    def uploadSpec = """
                    {
                        "files": [
                            {
                                "pattern": "*.zip",
                                "target": "${quater}__${year}__${env.BUILD_NUMBER}__GHE-Attestation__${timestamp}.zip", 
                                "recursive": "false",
                                "flat": "false",
                                "props": "build.version=${env.BUILD_NUMBER}"
                            }
                        ]
                    }
                    """
                    def buildInfo = server.upload spec: uploadSpec
                    server.publishBuildInfo buildInfo
                }
            }
        }
    }
}
