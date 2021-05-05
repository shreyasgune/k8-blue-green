Note: When running on GKE (Google Kubernetes Engine), you may encounter a ‘permission denied’ error when creating some of these resources. This is a nuance of the way GKE handles RBAC and IAM permissions, and as such you should ‘elevate’ your own privileges to that of a ‘cluster-admin’ before running the above command.
```
  kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole=cluster-admin \
    --user=$(gcloud config get-value core/account)
```

```
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.3.1/cert-manager.yaml
```

## Verify
```
kubectl apply -f local-k8/ssl/test.yaml

kubectl describe certificate -n cert-manager-test
    Name:         selfsigned-cert
Namespace:    cert-manager-test
Labels:       <none>
Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"cert-manager.io/v1","kind":"Certificate","metadata":{"annotations":{},"name":"selfsigned-cert","namespace":"cert-manager-te...
API Version:  cert-manager.io/v1
Kind:         Certificate
Metadata:
  Creation Timestamp:  2021-05-05T15:55:37Z
  Generation:          1
  Resource Version:    1075
  Self Link:           /apis/cert-manager.io/v1/namespaces/cert-manager-test/certificates/selfsigned-cert
  UID:                 c86208cf-4945-4044-aabc-6486bca636f1
Spec:
  Dns Names:
    example.com
  Issuer Ref:
    Name:       test-selfsigned
  Secret Name:  selfsigned-cert-tls
Status:
  Conditions:
    Last Transition Time:  2021-05-05T15:55:38Z
    Message:               Certificate is up to date and has not expired
    Observed Generation:   1
    Reason:                Ready
    Status:                True
    Type:                  Ready
  Not After:               2021-08-03T15:55:38Z
  Not Before:              2021-05-05T15:55:38Z
  Renewal Time:            2021-07-04T15:55:38Z
  Revision:                1
Events:
  Type    Reason     Age   From          Message
  ----    ------     ----  ----          -------
  Normal  Issuing    45s   cert-manager  Issuing certificate as Secret does not exist
  Normal  Generated  44s   cert-manager  Stored new private key in temporary Secret resource "selfsigned-cert-xdlkv"
  Normal  Requested  44s   cert-manager  Created new CertificateRequest resource "selfsigned-cert-8wdqj"
  Normal  Issuing    44s   cert-manager  The certificate has been successfully issued
```

## Apply your SSL Manifests
```
kubectl apply -f local-k8/ssl/issuer.yaml
kubectl apply -f local-k8/ssl/ingress.yaml

    ingress.extensions/ingressrule created
    issuer.cert-manager.io/letsencrypt-staging created

```

- Verfiy
```
kubectl describe issuer letsencrypt-staging
Name:         letsencrypt-staging
Namespace:    default
Labels:       <none>
Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"cert-manager.io/v1","kind":"Issuer","metadata":{"annotations":{},"name":"letsencrypt-staging","namespace":"default"},"spec"...
API Version:  cert-manager.io/v1
Kind:         Issuer
Metadata:
  Creation Timestamp:  2021-05-05T17:43:02Z
  Generation:          1
  Resource Version:    3345
  Self Link:           /apis/cert-manager.io/v1/namespaces/default/issuers/letsencrypt-staging
  UID:                 eb8075ea-893f-4e4d-9775-023121aded23
Spec:
  Acme:
    Email:            sgune@pm.me
    Preferred Chain:
    Private Key Secret Ref:
      Name:  account-key-staging
    Server:  https://acme-staging-v02.api.letsencrypt.org/directory
    Solvers:
      http01:
        Ingress:
          Class:  nginx
Status:
  Acme:
    Last Registered Email:  sgune@pm.me
    Uri:                    https://acme-staging-v02.api.letsencrypt.org/acme/acct/19393139
  Conditions:
    Last Transition Time:  2021-05-05T17:43:03Z
    Message:               The ACME account was registered with the ACME server
    Observed Generation:   1
    Reason:                ACMEAccountRegistered
    Status:                True
    Type:                  Ready
Events:                    <none>

kubectl get ingress
NAME          HOSTS                      ADDRESS         PORTS     AGE
ingressrule   staging.blizz-server.com   192.168.64.33   80, 443   14m

```
## Test
```
curl --request GET \
  --url https://192.168.64.33/version \
  --header 'host: staging.blizz-server.com'

 TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.2 (IN), TLS handshake, Certificate (11):
* TLSv1.2 (IN), TLS handshake, Server key exchange (12):
* TLSv1.2 (IN), TLS handshake, Server finished (14):
* TLSv1.2 (OUT), TLS handshake, Client key exchange (16):
* TLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.2 (OUT), TLS handshake, Finished (20):
* TLSv1.2 (IN), TLS handshake, Finished (20):
* SSL connection using TLSv1.2 / ECDHE-RSA-AES256-GCM-SHA384
* ALPN, server accepted to use h2
* Server certificate:
*  subject: O=Acme Co; CN=Kubernetes Ingress Controller Fake Certificate
*  start date: May  5 17:22:26 2021 GMT
*  expire date: May  5 17:22:26 2022 GMT
*  issuer: O=Acme Co; CN=Kubernetes Ingress Controller Fake Certificate
*  SSL certificate verify result: self signed certificate (18), continuing anyway.
* Using HTTP2, server supports multi-use
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* Using Stream ID: 1 (easy handle 0x7f99c8309000)
```