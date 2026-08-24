pipeline {
  agent any

  environment {
    // From the host's Docker daemon (Jenkins builds/pushes via the mounted
    // socket), so "localhost" is correct here — this is NOT what the
    // manifests reference (they use host.minikube.internal).
    IMAGE = "localhost:5050/root/jarvis-conversation-service"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        // env.GIT_COMMIT is unreliable — see jarvis-backend's Jenkinsfile
        // for why this reads the workspace's actual HEAD instead.
        script {
          env.IMAGE_TAG = sh(script: 'git rev-parse --short=8 HEAD', returnStdout: true).trim()
        }
      }
    }

    stage('Build image') {
      steps {
        sh "docker build -t ${IMAGE}:${IMAGE_TAG} ."
      }
    }

    stage('Push image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'gitlab-registry', usernameVariable: 'REG_USER', passwordVariable: 'REG_PASS')]) {
          sh 'echo "$REG_PASS" | docker login localhost:5050 -u "$REG_USER" --password-stdin'
          sh "docker push ${IMAGE}:${IMAGE_TAG}"
        }
      }
    }

    stage('Bump manifest') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'gitlab-repo', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
          sh '''
            rm -rf deploy-repo
            git clone "http://${GIT_USER}:${GIT_TOKEN}@gitlab:8929/root/jarvis-deploy.git" deploy-repo
            cd deploy-repo/conversation-service/overlays/test
            kustomize edit set image jarvis-conversation-service=host.minikube.internal:5050/root/jarvis-conversation-service:${IMAGE_TAG}
            cd ../../..
            git config user.email "jenkins@localhost"
            git config user.name "jenkins-bot"
            git add conversation-service/overlays/test/kustomization.yaml
            git diff --cached --quiet && echo "no manifest changes" && exit 0
            git commit -m "ci: bump jarvis-conversation-service to ${IMAGE_TAG}"
            git push "http://${GIT_USER}:${GIT_TOKEN}@gitlab:8929/root/jarvis-deploy.git" HEAD:main
          '''
        }
      }
    }
  }
}
