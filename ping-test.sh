#! /bin/bash
watch -n 3 "curl -s $(minikube service blizz-server --url)/version"