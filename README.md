# k8-blue-green
This repo contains a sample python server and the deployment manifests.


## Local Testing

### Docker Build and Push
```
docker build --build-arg BLIZZ_VERSION=test  -t shreyasgune/blizz-server:test .
```
> Note that the build-argument passed is the version of the application, and it gets read into the server as an environment variable.

```
docker login <credentials>
docker push shreyasgune/blizz-server:test
```
### [Minikube](https://minikube.sigs.k8s.io/docs/start/)
[Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
```
minikube start --memory=16384 --cpus=4
😄  minikube v1.5.2 on Darwin 10.14.6
✨  Automatically selected the 'hyperkit' driver
🔥  Creating hyperkit VM (CPUs=4, Memory=16384MB, Disk=20000MB) ...
🐳  Preparing Kubernetes v1.16.2 on Docker '18.09.9' ...
🚜  Pulling images ...
🚀  Launching Kubernetes ...
⌛  Waiting for: apiserver
🏄  Done! kubectl is now configured to use "minikube"
```
> yours should look similar, but not exact.

### Deploy Locally and Test it
> Go through the manifests in `local-k8` directory before applying
```
kubectl apply -f local-k8
deployment.apps/blizz-server-test created
service/blizz-server created
```

Testing
```
minikube service blizz-server --url
curl $(minikube service blizz-server --url)/version

## The problem statement
```
i.            Start v1 of the application

ii.            Write a simple test client to call {service_base_url}/version repeatedly

iii.            Update the version of the sample application

iv.            Utilize your deployment strategy to execute a blue/green deploy of test application v2

v.            Capture the output of your test client to show that no requests failed and the version being returned from the sample application changed
```