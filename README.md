# k8-blue-green
This repo contains a sample python server and the deployment manifests.

## [Minikube](https://minikube.sigs.k8s.io/docs/start/)
[Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
```
minikube start --memory=16384 --cpus=4
```

## The problem statement
```
i.            Start v1 of the application

ii.            Write a simple test client to call {service_base_url}/version repeatedly

iii.            Update the version of the sample application

iv.            Utilize your deployment strategy to execute a blue/green deploy of test application v2

v.            Capture the output of your test client to show that no requests failed and the version being returned from the sample application changed
```