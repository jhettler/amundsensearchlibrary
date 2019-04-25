@Library('lmc-jenkins2-shared-library@master')
@Library('bi-jenkins2-shared-libraries@master') _

import eu.lmc.pipeline.DockerRegistry

pipeline {
  agent any

  options {
    timeout( time: 30, unit: 'MINUTES') //  build timeout
    disableConcurrentBuilds() // disable multiple concurent builds
  }

  parameters {
    string(name: 'image_name', defaultValue: 'lmc-bi-amundsen-search')
    string(name: 'project_url', defaultValue: 'https://stash.int.lmc.cz/projects/BI/repos/amundsensearchlibrary')
    booleanParam(name: 'deploy_image', defaultValue: false, description: 'Should be image deleted/deployed to DEV/PROD servers?')
    string(name: 'slack_channel', defaultValue: '#bi-prod')
    string(name: 'container_name', defaultValue: 'admundsen-search')
    string(name: 'amundsen_base_folder', defaultValue: '/usr/local/amundsen')
  }

  stages {
    stage('Notification') {
      when {
        beforeAgent true
        anyOf {
          branch 'test'
          branch 'master'
        }
      }
      steps {
        script {
          // notify just in case of deployment and master and test branches
          if (params.deploy_image) {
            sendBuildNotification('STARTED', "${params.slack_channel}", "${params.project_url}")
          }
        }
      }
    }

    stage('Prepare') {
      steps {
        script {
          enviro = getEnvironment()
          (masters,workers) = getBIServers()
          servers = masters + workers
          registry = getRegistry()
          def currentDate = sh(returnStdout: true, script: 'date +"%Y.%m.%d.%H%M%S"').trim()
          gitCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
          def shortCommit = gitCommit.take(11)
          buildVersion = "${currentDate}-g${shortCommit}-${env.BUILD_NUMBER}"
          println "Version: ${buildVersion}"
        }
      }
    }

    stage('Build image') {
      steps {
        script {
            dockerRegistry = new DockerRegistry(this).login('dcreg.service.consul')
            def otherParams = "--label build_version=${buildVersion} --label build_branch=${env.BRANCH_NAME} --label build_url=${BUILD_URL} --label build_type=${enviro.toLowerCase()}"
            dockerImage = docker.build("${params.image_name}", "-f Dockerfile $otherParams .")
        }
      }
    }

    stage('Push image') {
      when {
        beforeAgent true
        anyOf {
          branch 'test'
          branch 'master'
        }
      }
      steps {
        script {
            dockerImageToInstall = tagAndPushImageSerialIfNotExist("${enviro.toLowerCase()}", "${params.image_name}", "${buildVersion}")
        }
      }
      post {
        success {
          script {
            sh "docker rmi --force `docker images -q ${params.image_name} | uniq`"
          }
        }
      }
    }

    stage('Deploy image') {
      when {
        beforeAgent true
        anyOf {
          branch 'test'
          branch 'master'
        }
      }
      steps {
        script {
          if (params.deploy_image) {
            sendDeployNotification("${params.slack_channel}", "${enviro}", "${params.image_name}", "${buildVersion}", "${registry}", "${servers}")
            masters.each { master ->
              def stopServices = "ssh -o StrictHostKeyChecking=no airflow@${master} \"docker rm ${params.container_name} -f || true\""
              def rmImg = "ssh -o StrictHostKeyChecking=no airflow@${master} \"docker rmi ${registry}/${params.image_name}:latest -f || true\""
              def pullImg = "ssh -o StrictHostKeyChecking=no airflow@${master} \"docker pull ${registry}/${params.image_name}:latest\""
              sshagent (credentials: ['37c018e2-e1c9-46bd-85cf-c1d14017a9c9']) {
                sh(returnStdout: true, script:stopServices)
                sh(returnStdout: true, script:rmImg)
                sh(returnStdout: true, script:pullImg)
              }
            }
            sh(returnStdout: true, script: "git tag -d released/${enviro} || true")
            sh(returnStdout: true, script: "git push --delete origin released/${enviro} || true")
            sh(returnStdout: true, script: "git tag released/${enviro} || true")
            sh(returnStdout: true, script: "git tag ${buildVersion} || true")
            sh(returnStdout: true, script: "git push --tags || true")
          }
        }
      }
    }
    stage ("Pulling dokcer-compose") {
      when {
        beforeAgent true
        anyOf {
          branch 'test'
          branch 'master'
        }
      }
      steps {
        sh 'mkdir -p frontend'
        dir("frontend")
        {
            git branch: "master",
            credentialsId: '5e85bf3f-0ae6-4143-8e1a-2cf428909622',
            url: 'ssh://@git@stash.int.lmc.cz:7999/bi/amundsenfrontendlibrary.git'
        }
      }
    }

    stage ("Distributing docker-compose") {
      when {
        beforeAgent true
        anyOf {
          branch 'test'
          branch 'master'
        }
      }
      steps {
        script {
          masters.each { master ->
            def createAmundsenDir= "ssh -o StrictHostKeyChecking=no airflow@${master} \"mkdir -p ${params.amundsen_base_folder}\""
            def copyStaticDir= "scp -r ./frontend/docker-amundsen.yml airflow@${master}:${params.amundsen_base_folder}/"
            def copyConfigDir= "scp -r ./frontend/example/* airflow@${master}:${params.amundsen_base_folder}/example/"
            sshagent (credentials: ['37c018e2-e1c9-46bd-85cf-c1d14017a9c9']) {
                sh(returnStdout: true, script:createAmundsenDir)
                sh(returnStdout: true, script:copyStaticDir)
                sh(returnStdout: true, script:copyConfigDir)
            }
          }
        }
      }
    }    

    stage ("Starting services") {
      when {
        beforeAgent true
        anyOf {
          branch 'test'
          branch 'master'
        }
      }
      steps {
        script {
          //if (params.deploy_image) {
            masters.each { master ->
              def runCont = "ssh -o StrictHostKeyChecking=no airflow@${master} \"cd /usr/local/amundsen && docker-compose -f docker-amundsen.yml up -d\""
              sshagent (credentials: ['37c018e2-e1c9-46bd-85cf-c1d14017a9c9']) {
                sh(returnStdout: true, script:runCont)
              }
            }
          //}
        }
      }
    }
  }
  post {
    always {
      script {
        if (params.deploy_image || currentBuild.result == 'FAILURE' ) {
          sendBuildNotification(currentBuild.result, "${params.slack_channel}", "${params.project_url}")
        }
        currentBuild.result = currentBuild.result ?: 'SUCCESS'
        notifyBitbucket()
        deleteDir()
      }
    }
  }
}
