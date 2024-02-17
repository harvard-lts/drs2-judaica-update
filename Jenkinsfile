#!groovy
@Library('lts-basic-pipeline') _

// projName is the directory name for the project on the servers for it's docker/config files
// default values: 
//  registryCredentialsId = "${env.REGISTRY_ID}"
//  registryUri = 'https://registry.lts.harvard.edu'
def endpoints = [""]
ltsBasicPipeline.call("drs2-judaica-update", "ETD", "drsadm", "10610", endpoints, "lts-jenkins-notifications")
