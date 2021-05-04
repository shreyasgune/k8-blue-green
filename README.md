# k8-blue-green
This repo contains a sample python server and the deployment manifests.

### Job Statuses
**Container Build and Test Jobs**

![Image Build and Push](https://github.com/shreyasgune/k8-blue-green/workflows/Image%20Publish/badge.svg)
![Image Test](https://github.com/shreyasgune/k8-blue-green/workflows/Image%20Test/badge.svg)
![Security Scan](https://github.com/shreyasgune/k8-blue-green/workflows/Security%20Scan/badge.svg)

**Deploy Jobs**

![Minikube Test](https://github.com/shreyasgune/k8-blue-green/workflows/Minikube%20Test/badge.svg)
![GKE Deploy](https://github.com/shreyasgune/k8-blue-green/workflows/GKE%20Deploy/badge.svg)
![Switch Traffic](https://github.com/shreyasgune/k8-blue-green/workflows/Switch%20Traffic/badge.svg)


**Genereal Purpose Scan Jobs**

![CodeQL Scan](https://github.com/shreyasgune/k8-blue-green/workflows/CodeQL/badge.svg)
[![Snyk Container](https://github.com/shreyasgune/k8-blue-green/actions/workflows/snyk-container-analysis.yml/badge.svg)](https://github.com/shreyasgune/k8-blue-green/actions/workflows/snyk-container-analysis.yml)

## Local Testing

### Run the app and test
- app exec
```
cd app
pip install --upgrade pip
pip install -r requirements.txt
python th3-server.py
```

- curl tests
```
curl -s http://localhost:8080/version
    {"version": "test", "errors": []}

curl -s http://localhost:8080/api/v1/translate\?phrase\=Lol
    {"phrase": "Lol", "translation": "Kek", "errors": []}

```


### Docker Build and Push

Image Repo: [shreyasgune/blizz-server](https://hub.docker.com/repository/docker/shreyasgune/blizz-server)

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
curl -s $(minikube service blizz-server --url)/version
    {"version": "test", "errors": []}
```

Testing Redis if using `assets/redis` manifests
```
Shell 1:
kubectl port-forward svc/redis-master 6379:6379
Forwarding from 127.0.0.1:6379 -> 6379
Forwarding from [::1]:6379 -> 6379
Handling connection for 6379

Shell 2:
redis-cli -h localhost -p 6379
localhost:6379> PING
PONG
```

## Testing BLUE-GREEN
- Build, test & push Blue Image
```
docker build --build-arg BLIZZ_VERSION=blue  -t shreyasgune/blizz-server:blue .
docker run -d -p 8080:8080 --name sgune-blizz-blue  -it shreyasgune/blizz-server:blue
curl http://localhost:8080/version
    {"version": "blue", "errors": []}
docker push docker.io/shreyasgune/blizz-server:blue
docker rm -f sgune-blizz-blue
```

- Build, test & push Green Image
```
docker build --build-arg BLIZZ_VERSION=green  -t shreyasgune/blizz-server:green .
docker run -d -p 8080:8080 --name sgune-blizz-green  -it shreyasgune/blizz-server:green
curl http://localhost:8080/version
    {"version": "green", "errors": []}
docker push docker.io/shreyasgune/blizz-server:green
docker rm -f sgune-blizz-green
```
 
- Deploy Blue to Minikube
```
sed 's/{{BLIZZ_VERSION}}/blue/g' k8s/*.yaml > blue.yaml && kubectl apply -f blue.yaml
deployment.apps/blizz-server-blue created
service/blizz-server created
```

- Start a ping test in a separate shell
```
./ping-test.sh
```

- Deploy Green to Minikube
```
sed 's/{{BLIZZ_VERSION}}/blue/g' k8s/*.yaml > blue.yaml && kubectl apply -f green.yaml
deployment.apps/blizz-server-green created
service/blizz-server changed
```

>Observe the ouput on the `ping-test.sh` shell

- Cleanup
```
rm -f blue.yaml
rm -f green.yaml
```

## Github Actions
You can also run the following jobs if you don't wish to do local-testing
- `app-build-push` workflow: Builds the image with a certain version number, tags it and pushes it to image repository
- `test-image` workflow: Tests a particular version of an existing image
- `minikube-test` workflow
    - Creates a sandboxed Minikube cluster of 1 on the github-runner
    - Deploys a particular version in Minikube
    - Tests it
- `gke-deploy` workflow: takes a version and deploys it to the `blizz-cluster` in GKE
- `switch-traffic` workflow: switches traffic to a certain version of deployment
- `security-scan` workflow: scans the image tag via version, tells you about the vulnerabilities

# Deploy and Test to GKE
Use the Github Actions jobs to deploy and test a certain version of your app.

[Example Job Run](https://github.com/shreyasgune/k8-blue-green/runs/2501600504?check_suite_focus=true)

- Cluster
![](assets/images/cluster.png)
- Deployment
![](assets/images/deployment.png)
- Services
![](assets/images/svc.png)


## Future Work
- HELM
    > I know that `sed` substitution is wonky and `helm` is the way to go. I just need to do it over the next weekend. HELM2 vs HELM3 has thrown me off into a time sink before so I kinda wanted to get this first draft out ASAP.
- Getting Terraform to work, [files found here](assets/gke-tf.yaml)
- Speaking with [Redis Deployment](assets/redis-cluster-manifests)
- Redis Investigation
```
Shell 1:
λ docker run -p 6379:6379 --name gman-redis redis 
1:C 04 May 2021 19:59:35.730 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:C 04 May 2021 19:59:35.730 # Redis version=6.2.3, bits=64, commit=00000000, modified=0, pid=1, just started
1:C 04 May 2021 19:59:35.730 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
1:M 04 May 2021 19:59:35.731 * monotonic clock: POSIX clock_gettime
1:M 04 May 2021 19:59:35.732 * Running mode=standalone, port=6379.
1:M 04 May 2021 19:59:35.732 # Server initialized
1:M 04 May 2021 19:59:35.732 * Ready to accept connections

Shell 2:
λ redis-cli -h localhost -p 6379     
localhost:6379> ping
PONG
localhost:6379> monitor
OK
1620158768.174458 [0 172.17.0.3:53140] "HINCRBY" "requests_by_ip" "172.17.0.1" "1"
1620158769.793243 [0 172.17.0.3:53162] "HINCRBY" "requests_by_ip" "172.17.0.1" "1"
1620158770.478544 [0 172.17.0.3:53146] "HINCRBY" "requests_by_ip" "172.17.0.1" "1"

Shell 3:
λ export REDIS_ADDR=172.17.0.2                                 
λ docker run -p 8080:8080 --name sgune-blizz -e REDIS_ADDR=$REDIS_ADDR  shreyasgune/blizz-server:test
Bottle v0.12.19 server starting up (using GunicornServer(workers=4))...
Listening on http://0.0.0.0:8080/
Hit Ctrl-C to quit.

[2021-05-04 20:00:51 +0000] [1] [INFO] Starting gunicorn 20.1.0
[2021-05-04 20:00:51 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2021-05-04 20:00:51 +0000] [1] [INFO] Using worker: sync
[2021-05-04 20:00:51 +0000] [8] [INFO] Booting worker with pid: 8
[2021-05-04 20:00:51 +0000] [9] [INFO] Booting worker with pid: 9
[2021-05-04 20:00:51 +0000] [10] [INFO] Booting worker with pid: 10
[2021-05-04 20:00:51 +0000] [11] [INFO] Booting worker with pid: 11

Shell 4:
λ curl http://localhost:8080/version                            
{"version": "test", "errors": []}%

λ curl http://localhost:8080/api/v1/translate\?phrase\=Lol    
{"phrase": "Lol", "translation": "Kek", "errors": []}%
```


## The problem statement
```
i.            Start v1 of the application

ii.            Write a simple test client to call {service_base_url}/version repeatedly

iii.            Update the version of the sample application

iv.            Utilize your deployment strategy to execute a blue/green deploy of test application v2

v.            Capture the output of your test client to show that no requests failed and the version being returned from the sample application changed
```
