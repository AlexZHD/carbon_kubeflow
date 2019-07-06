# CarbonFlow
CarbonFlow - DevOps Fellow @ Insight
Deployment pipeline to KOPS Kubernetes for Carbon Emission ML model with versioning, monitoring

## Overview
Food waste and climate change are both major issues affecting our planet's future today. The problem is that emissions data is not available for all food products. Carbon Emission model aims to estimate how much carbon emissions are created by a given food or beverage product. The DevOps challenge is to provide a working Jenkins CI / CD deployment pipeline on KOPS Kubernetes for Carbon Emission ML model with versioning, monitoring

## Tech Stack
Technologies used: Teraform, Docker, KOPS, Kubernetes, Jenkins, Kubectl, Helm

## Required Tools
1. Terraform: https://learn.hashicorp.com/terraform/getting-started/install.html
2. KOPS: 
3. AWS-IAM: https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html
4. Kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/
5. Helm: https://github.com/helm/helm

## Required AWS Access
An AWS account with an access key is needed with the following permissions:
1. AmazonEC2FullAccess
2. IAMFullAccess
3. AmazonS3FullAccess
4. AmazonVPCFullAccess
5. AmazonRoute53FullAccess

## Setup AWS EC2 Key Pairs
```
# Open terminal and run ssh-keygen
sudo ssh-keygen

# Note key name - This will be used in terraform.tfvars file
# Import ssh public key to aws EC2 console
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
```

## Setup of AWS Infrastructure with Terraform and KOPS

```
# Clone repo

# CD to terraform code directory
cd carbon_kuberflow

# Initialize Terraform with
terraform init

# View and adjust terraform variables
# At minimum add aws access key, aws secret key, aws ssh key name, dockerhub login and pw
vi terraform.tfvars
export AWS_ACCESS_KEY_ID=<access key>
export AWS_SECRET_ACCESS_KEY=<secret key>

# Set github not to track terraform.tfvars file

# View and adjust terraform workspace variables
Before we run terraform apply, we need to configure some variables. In variables.tf, you need to set the name variable. It is used in several places in our configuration and should be set to the domain name you are going to be using for this cluster. You can either modify the variables.tf
Most of the heavy lifting is done in the vpc and subnet-pair modules (.modules)
Besides the networking infrastructure, we also need to create the hosted zone for our cluster domain name in Route53. If you are following along and already have your domain name registered in Route53, you can remove this resource from your local configuration.
resource "aws_route53_zone" "public" {
  name          = "${var.name}"
  force_destroy = true
  ...
}
Kops also requires an S3 bucket for storing the state of the cluster. We create this bucket as part of our Terraform configuration
resource "aws_s3_bucket" "state_store" {
  bucket        = "${var.name}-state"
  ...  
}

# Review infrustructure with
terraform plan

# Create infrustructure with
$terraform apply

Exaple of terraform ouput in us-west-2 region:
    Outputs:
    availability_zones = [
        us-west-2a,
        us-west-2b,
        us-west-2c
    ]
    cluster_name = staging.zdevops.xyz
    name = zdevops.xyz
    name_servers = [
        ns-1278.awsdns-31.org,
        ns-1914.awsdns-47.co.uk,
        ns-442.awsdns-55.com,
        ns-747.awsdns-29.net
    ]
    nat_gateway_ids = [
        nat-09c6443349efb1b51,
        nat-00a269e75f7850ffd,
        nat-0c6cbf17c78582d8b
    ]
    private_subnet_ids = [
        subnet-0987fa8181fe8de8f,
        subnet-0eac202e16a1fe976,
        subnet-0dd6bcd76fc14ecf8
    ]
    public_subnet_ids = [
        subnet-0827a52825abbb40f,
        subnet-06bd02a1b345c9782,
        subnet-03c054e41f91779e5
    ]
    public_zone_id = Z8KDEXQCJUM1H
    state_store = s3://zdevops.xyz-state
    vpc_id = vpc-021415f5b49d2a7dc

# export a few environment variables that we will be using in our Kops commands
export NAME=$(terraform output cluster_name)
    $echo $NAME
    staging.zdevops.xyz
export KOPS_STATE_STORE=$(terraform output state_store)
    $echo $KOPS_STATE_STORE
    s3://zdevops.xyz-state
$export ZONES=us-west-2a,us-west-2b,us-west-2c
    $echo $ZONES
    us-west-2a,us-west-2b,us-west-2c
# Now we can run Kops. Here is the command we will use to create our cluster:
$kops create cluster --master-zones $ZONES --zones $ZONES --topology private --node-size=t2.micro --master-size=t2.micro --dns-zone $(terraform output public_zone_id) --networking calico --vpc $(terraform output vpc_id) --target=terraform --out=. ${NAME}
    1)master-zones: tell Kops that we want one Kubernetes master in each zone in $ZONES. 
    2)zones: tells Kops that our Kubernetes nodes will live in those same availability zones.
    3)topology: tells Kops that we want to use a private network topology. Our Kubernetes instances will live in private subnets in each zone.
    4)dns-zone: specifies the zone ID for the domain name we registered in Route53. In this example, this is populated from our Terraform output but you can specify the zone ID manually if necessary.
    5)networking: we are using Calico for our cluster networking in this example. Since we are using a private topology, we cannot use the default kubenet mode.
    6)vpc: tells Kops which VPC to use. This is populated by a Terraform output in this example.
    7)target: tells Kops that we want to generate a Terraform configuration (rather than its default mode of managing AWS resources directly).
    8)out: specifies the output directory to write the Terraform configuration to. In this case, we just want to use the current directory.
# Review Kops output, exmplae below    
    I0620 00:55:48.610563   87055 create_cluster.go:496] Inferred --cloud=aws from zone "us-west-2a"
    I0620 00:55:49.328054   87055 subnets.go:184] Assigned CIDR 10.20.32.0/19 to subnet us-west-2a
    I0620 00:55:49.328112   87055 subnets.go:184] Assigned CIDR 10.20.64.0/19 to subnet us-west-2b
    I0620 00:55:49.328128   87055 subnets.go:184] Assigned CIDR 10.20.96.0/19 to subnet us-west-2c
    I0620 00:55:49.328141   87055 subnets.go:198] Assigned CIDR 10.20.0.0/22 to subnet utility-us-west-2a
    I0620 00:55:49.328154   87055 subnets.go:198] Assigned CIDR 10.20.4.0/22 to subnet utility-us-west-2b
    I0620 00:55:49.328166   87055 subnets.go:198] Assigned CIDR 10.20.8.0/22 to subnet utility-us-west-2c
    I0620 00:55:50.417439   87055 create_cluster.go:1407] Using SSH public key: /Users/bird5555/.ssh/id_rsa.pub
    W0620 00:55:52.935041   87055 firewall.go:250] Opening etcd port on masters for access from the nodes, for calico.  This is unsafe in untrusted environments.
    I0620 00:55:54.061362   87055 executor.go:103] Tasks: 0 done / 111 total; 35 can run
    I0620 00:55:54.063630   87055 dnszone.go:242] Check for existing route53 zone to re-use with name ""
    I0620 00:55:54.173579   87055 dnszone.go:249] Existing zone "zdevops.xyz." found; will configure TF to reuse
    I0620 00:55:56.625165   87055 vfs_castore.go:736] Issuing new certificate: "ca"
    I0620 00:55:56.937372   87055 vfs_castore.go:736] Issuing new certificate: "apiserver-aggregator-ca"
    I0620 00:55:57.602456   87055 executor.go:103] Tasks: 35 done / 111 total; 32 can run
    I0620 00:55:58.940253   87055 vfs_castore.go:736] Issuing new certificate: "kubelet"
    I0620 00:55:58.995460   87055 vfs_castore.go:736] Issuing new certificate: "kube-scheduler"
    I0620 00:55:58.997093   87055 vfs_castore.go:736] Issuing new certificate: "kube-proxy"
    I0620 00:55:59.082871   87055 vfs_castore.go:736] Issuing new certificate: "apiserver-aggregator"
    I0620 00:55:59.147471   87055 vfs_castore.go:736] Issuing new certificate: "kubelet-api"
    I0620 00:55:59.155851   87055 vfs_castore.go:736] Issuing new certificate: "master"
    I0620 00:55:59.235564   87055 vfs_castore.go:736] Issuing new certificate: "kubecfg"
    I0620 00:55:59.310205   87055 vfs_castore.go:736] Issuing new certificate: "kube-controller-manager"
    I0620 00:55:59.416704   87055 vfs_castore.go:736] Issuing new certificate: "kops"
    I0620 00:55:59.431499   87055 vfs_castore.go:736] Issuing new certificate: "apiserver-proxy-client"
    I0620 00:56:01.670699   87055 executor.go:103] Tasks: 67 done / 111 total; 30 can run
    I0620 00:56:02.054517   87055 executor.go:103] Tasks: 97 done / 111 total; 8 can run
    I0620 00:56:02.055433   87055 executor.go:103] Tasks: 105 done / 111 total; 6 can run
    I0620 00:56:02.055796   87055 executor.go:103] Tasks: 111 done / 111 total; 0 can run
    I0620 00:56:02.068571   87055 target.go:312] Terraform output is in .
    I0620 00:56:02.176553   87055 update_cluster.go:290] Exporting kubecfg for cluster
    kops has set your kubectl context to staging.zdevops.xyz
    Terraform output has been placed into .
    Changes may require instances to restart: kops rolling-update cluster
# What happened:
    1) Populating the KOPS_STATE_STORE S3 bucket with the Kubernetes cluster configuration
    2) Creating several record sets in the Route53 hosted zone for your domain (for Kubernetes APIs and etcd)
    3) Creating IAM policy files, user data scripts, and an SSH key in the ./data directory.
    4) Generating a Terraform configuration for all of the Kubernetes resources. This will be saved in a file called kubernetes.tf.
# The kubernetes.tf includes all of the resources required to deploy the cluster. 
We want to deploy Kubernetes in our existing subnets. need to edit the cluster  configuration so that Kops knows about our existing network resources
    $terraform output -json nat_gateway_ids
    {
        "sensitive": false,
        "type": "list",
        "value": [
            "nat-09c6443349efb1b51",
            "nat-00a269e75f7850ffd",
            "nat-0c6cbf17c78582d8b"
        ]
    }
    $terraform output -json private_subnet_ids
    {
        "sensitive": false,
        "type": "list",
        "value": [
            "subnet-0987fa8181fe8de8f",
            "subnet-0eac202e16a1fe976",
            "subnet-0dd6bcd76fc14ecf8"
        ]
    }
    $terraform output -json public_subnet_ids
    {
        "sensitive": false,
        "type": "list",
        "value": [
            "subnet-0827a52825abbb40f",
            "subnet-06bd02a1b345c9782",
            "subnet-03c054e41f91779e5"
        ]
    }
# Run KOPS edit to replace the subnets section with our existing vpc and subnet information
There should be one Private type subnet and one Utility (public) type subnet in each availability zone. We need to modify this section by replacing each cidr with the corresponding existing subnet ID for that region. For the Private subnets, we also need to specify our NAT gateway ID in an egress key
$kops edit cluster ${NAME}
subnets map should look something like this: 
  - egress: nat-09c6443349efb1b51
    id: subnet-0987fa8181fe8de8f
    name: us-west-2a
    type: Private
    zone: us-west-2a
  - egress: nat-00a269e75f7850ffd
    id: subnet-0eac202e16a1fe976
    name: us-west-2b
    type: Private
    zone: us-west-2b
  - egress: nat-0c6cbf17c78582d8b
    id: subnet-0dd6bcd76fc14ecf8
    name: us-west-2c
    type: Private
    zone: us-west-2c
  - id: subnet-0827a52825abbb40f
    name: utility-us-west-2a
    type: Utility
    zone: us-west-2a
  - id: subnet-06bd02a1b345c9782
    name: utility-us-west-2b
    type: Utility
    zone: us-west-2b
  - id: subnet-03c054e41f91779e5
    name: utility-us-west-2c
    type: Utility
    zone: us-west-2c       
# have not yet updated the kubernetes.tf file. To do that, we need to run kops update cluster:
$kops update cluster \
  --out=. \
  --target=terraform \
  ${NAME}
    W0620 01:13:30.770531   87423 firewall.go:250] Opening etcd port on masters for access from the nodes, for calico.  This is unsafe in untrusted environments.
    I0620 01:13:32.006367   87423 executor.go:103] Tasks: 0 done / 91 total; 35 can run
    I0620 01:13:32.008948   87423 dnszone.go:242] Check for existing route53 zone to re-use with name ""
    I0620 01:13:32.123541   87423 dnszone.go:249] Existing zone "zdevops.xyz." found; will configure TF to reuse
    I0620 01:13:33.505535   87423 executor.go:103] Tasks: 35 done / 91 total; 28 can run
    I0620 01:13:34.011228   87423 executor.go:103] Tasks: 63 done / 91 total; 20 can run
    I0620 01:13:34.463874   87423 executor.go:103] Tasks: 83 done / 91 total; 5 can run
    I0620 01:13:34.464429   87423 executor.go:103] Tasks: 88 done / 91 total; 3 can run
    I0620 01:13:34.464629   87423 executor.go:103] Tasks: 91 done / 91 total; 0 can run
    I0620 01:13:34.474794   87423 target.go:312] Terraform output is in .
    I0620 01:13:34.582187   87423 update_cluster.go:290] Exporting kubecfg for cluster
    kops has set your kubectl context to staging.zdevops.xyz
    Terraform output has been placed into .
    Changes may require instances to restart: kops rolling-update cluster
# If you look at the updated kubernetes.tf, you will see that it references our existing VPC infrastructure instead of creating new resources
# terraform plan
    Plan: 44 to add, 0 to change, 0 to destroy.
# terraform apply
    Outputs:
    availability_zones = [
        us-west-2a,
        us-west-2b,
        us-west-2c
    ]
    cluster_name = staging.zdevops.xyz
    master_autoscaling_group_ids = [
        master-us-west-2a.masters.staging.zdevops.xyz,
        master-us-west-2b.masters.staging.zdevops.xyz,
        master-us-west-2c.masters.staging.zdevops.xyz
    ]
    master_security_group_ids = [
        sg-0c2ec0cd6c122b393
    ]
    masters_role_arn = arn:aws:iam::205549526957:role/masters.staging.zdevops.xyz
    masters_role_name = masters.staging.zdevops.xyz
    name = zdevops.xyz
    name_servers = [
        ns-1278.awsdns-31.org,
        ns-1914.awsdns-47.co.uk,
        ns-442.awsdns-55.com,
        ns-747.awsdns-29.net
    ]
    nat_gateway_ids = [
        nat-09c6443349efb1b51,
        nat-00a269e75f7850ffd,
        nat-0c6cbf17c78582d8b
    ]
    node_autoscaling_group_ids = [
        nodes.staging.zdevops.xyz
    ]
    node_security_group_ids = [
        sg-057be2962c9dd1083
    ]
    node_subnet_ids = [
        subnet-0987fa8181fe8de8f,
        subnet-0dd6bcd76fc14ecf8,
        subnet-0eac202e16a1fe976
    ]
    nodes_role_arn = arn:aws:iam::205549526957:role/nodes.staging.zdevops.xyz
    nodes_role_name = nodes.staging.zdevops.xyz
    private_subnet_ids = [
        subnet-0987fa8181fe8de8f,
        subnet-0eac202e16a1fe976,
        subnet-0dd6bcd76fc14ecf8
    ]
    public_subnet_ids = [
        subnet-0827a52825abbb40f,
        subnet-06bd02a1b345c9782,
        subnet-03c054e41f91779e5
    ]
    public_zone_id = Z8KDEXQCJUM1H
    region = us-west-2
    state_store = s3://zdevops.xyz-state
    subnet_ids = [
        subnet-03c054e41f91779e5,
        subnet-06bd02a1b345c9782,
        subnet-0827a52825abbb40f,
        subnet-0987fa8181fe8de8f,
        subnet-0dd6bcd76fc14ecf8,
        subnet-0eac202e16a1fe976
    ]
    subnet_us-west-2a_id = subnet-0987fa8181fe8de8f
    subnet_us-west-2b_id = subnet-0eac202e16a1fe976
    subnet_us-west-2c_id = subnet-0dd6bcd76fc14ecf8
    subnet_utility-us-west-2a_id = subnet-0827a52825abbb40f
    subnet_utility-us-west-2b_id = subnet-06bd02a1b345c9782
    subnet_utility-us-west-2c_id = subnet-03c054e41f91779e5
    vpc_id = vpc-021415f5b49d2a7dc        
# verify $cat ~/.kube/config  
you should see name of cluster as sample
- name: staging.zdevops.xyz 
# input hosted zones information in name cheap domain as TS records
# $host -t NS staging.zdevops.xyz
    #old info 
    staging.zdevops.xyz name server ns-388.awsdns-48.com.
    staging.zdevops.xyz name server ns-847.awsdns-41.net.
    staging.zdevops.xyz name server ns-1133.awsdns-13.org.
    staging.zdevops.xyz name server ns-1815.awsdns-34.co.uk.
    new one?
    Host staging.zdevops.xyz not found: 2(SERVFAIL)
# validate cluster 
$kops validate cluster --state=$(terraform output state_store)
    waiting for
        Using cluster from kubectl context: staging.zdevops.xyz

        Validating cluster staging.zdevops.xyz

        INSTANCE GROUPS
        NAME                    ROLE    MACHINETYPE     MIN     MAX     SUBNETS
        master-us-west-2a       Master  t2.micro        1       1       us-west-2a
        master-us-west-2b       Master  t2.micro        1       1       us-west-2b
        master-us-west-2c       Master  t2.micro        1       1       us-west-2c
        nodes                   Node    t2.micro        2       2       us-west-2a,us-west-2b,us-west-2c

        NODE STATUS
        NAME                                            ROLE    READY
        ip-10-20-101-115.us-west-2.compute.internal     node    True
        ip-10-20-101-135.us-west-2.compute.internal     master  True
        ip-10-20-102-184.us-west-2.compute.internal     master  True
        ip-10-20-103-130.us-west-2.compute.internal     master  True
        ip-10-20-103-203.us-west-2.compute.internal     node    True

        Your cluster staging.zdevops.xyz is ready
    $kubectl get nodes
        NAME                                          STATUS   ROLES    AGE   VERSION
        ip-10-20-101-115.us-west-2.compute.internal   Ready    node     3m    v1.11.10
        ip-10-20-101-135.us-west-2.compute.internal   Ready    master   4m    v1.11.10
        ip-10-20-102-184.us-west-2.compute.internal   Ready    master   4m    v1.11.10
        ip-10-20-103-130.us-west-2.compute.internal   Ready    master   4m    v1.11.10
        ip-10-20-103-203.us-west-2.compute.internal   Ready    node     3m    v1.11.10  
    
    The command to delete the Kubernetes cluster is:
        $kops delete cluster --state=$(terraform output state_store)
    $kubectl cluster-info  
        Kubernetes master is running at https://api.staging.zdevops.xyz
        KubeDNS is running at https://api.staging.zdevops.xyz/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
        To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'. 
    $kubectl version  
        Client Version: version.Info{Major:"1", Minor:"14", GitVersion:"v1.14.1", GitCommit:"b7394102d6ef778017f2ca4046abbaa23b88c290", GitTreeState:"clean", BuildDate:"2019-04-08T17:11:31Z", GoVersion:"go1.12.1", Compiler:"gc", Platform:"darwin/amd64"}
        Server Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.10", GitCommit:"7a578febe155a7366767abce40d8a16795a96371", GitTreeState:"clean", BuildDate:"2019-05-01T04:05:01Z", GoVersion:"go1.10.8", Compiler:"gc", Platform:"linux/amd64"}
    simple echo service deployment
        $kubectl run hello-kubernetes --image=k8s.gcr.io/echoserver:1.4 --port=8080
        $kubectl expose deployment hello-kubernetes --type=NodePort
        $kubectl get services    
    $kubectl get pods
    $kubectl get deployments 
    $kubectl exec -it hello-kubernetes -c web -- sh                
```
## Dockerfile to build the Carbon emission model with Flask and Sklearn
    at .\food_facts directory

    FROM python:3.6.3
    ENV PYTHONUNBUFFERED 1
    ENV SERVICE_NAME carbon
    # ENV API_VERSION 1
    ARG API_VERSION
    ENV API_VERSION=${API_VERSION}
    RUN mkdir -p /usr/src/app
    COPY *.joblib /usr/src/app/
    COPY *.py /usr/src/app/
    COPY requirements.txt /usr/src/app/
    WORKDIR /usr/src/app
    RUN pip install -r requirements.txt
    RUN pip install joblib
    EXPOSE 5000
    CMD ["python", "app.py"]

    # API_VERSION environment variable is used to handle versions of ML model.
    # example of local build canary vesion 2:
        $docker build . -t bird5555/carbon-api-canary --build-arg API_VERSION=2
    # example of build production version 3:
        $docker build . -t bird5555/carbon-api --build-arg API_VERSION=3
    # local run production API:    
        $docker run -d --name carbon-api -p 5000:5000 bird5555/carbon-api
    # initial test with curl for Cookies Tout Choco:
        $curl http://localhost:5000/carbon/v3/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
    # should get reply as:
        # {
        #     "prediction,v3": [
        #         318.3333333333333
        #     ]
        # }    
    # example to push docker file to docker registry:
        $docker push bird5555/carbon-api
        $docker push bird5555/carbon-api:tagname

## Launching the Containerised Flask ML Model Service on the minikube        
    # Minikube allows a single node Kubernetes cluster to run within a Virtual 
    # Machine (VM) within a local machine (i.e. on your laptop), for development 
    # purposes. On Mac OS X, the steps required to get up-and-running are as follows:
        #  make sure the Homebrew package manager for OS X is installed
        #  install VirtualBox using, brew cask install virtualbox
        #  install Minikube using, brew cask install minikube
    # start minikube as:
        $minikube start --memory 4096
        $kubectl config use-context minikube
        $kubectl cluster-info
            # Kubernetes master is running at https://192.168.99.106:8443
            # KubeDNS is running at https://192.168.99.106:8443/api/v1/namespaces/kube-system/# services/kube-dns:dns/proxy
        # run container with ML load in minikube pod managed by a replication controller, which is the device that 
        # ensures that at least one pod running api service is operational at any given time  
                # docker push bird5555/carbon-api 
                $kubectl delete deployment --all
                $kubectl delete services --all
                $minikube delete
                $rm -rf ~/.minikube
                $minikube start --memory 4096
            $kubectl run carbon-api --image=bird5555/carbon-api:latest --port=5000 --generator=run/v1
                kubectl run --generator=run/v1 is DEPRECATED and will be removed in a future version. Use kubectl run --generator=run-pod/v1 or kubectl create instead.
                replicationcontroller/carbon-api created
            $kubectl run carbon-api --image=bird5555/carbon-api:latest --port=5000 --generator=run-pod/v1  
            $kubectl get pods
                # NAME               READY   STATUS              RESTARTS   AGE
                # carbon-api-7d67cbc7cb-b5757   1/1     Running   0          36m
            # use port forwarding to test an individual container without exposing it to the 
            # public internet    
                $kubectl port-forward carbon-api-7d67cbc7cb-b5757 5000:5000  
            $curl http://localhost:5000/carbon/v1/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
            #To expose the container as a (load balanced) service to the outside world
            $kubectl expose replicationcontroller carbon-api --type=LoadBalancer --name carbon-api-http
            #check that this has worked and to find the services’s external IP address run
                $minikube service list
            # Minikube-specific commands as Minikube does not setup a real-life load balancer 
            # (which is what would happen if we made this request on a cloud platform)    
                $kubectl delete rc ...api
                $kubectl delete service ...api-http
                $minikube delete    

## Defining entire applications is with YAML files that are posted to the Kubernetes API
    # Directory .\py-flask-ml-carbon-api incudes YAMLs files for production and canary enviroments.
    # Example to apply production YAML to k8s :
    
        apiVersion: v1
        kind: Namespace
        metadata:
        name: prod-ml-app
        ---
        apiVersion: v1
        kind: ReplicationController
        metadata:
        name: prod-ml-predict-rc
        labels:
            app: prod-ml-predict
            env: prod    
        namespace: prod-ml-app
        spec:
        replicas: 2
        template:
            metadata:
            labels:
                app: prod-ml-predict
                env: prod
            namespace: prod-ml-app
            spec:
            containers:
            - image: bird5555/carbon-api
                name: prod-ml-predict-api
                ports:
                - containerPort: 5000
                protocol: TCP
        ---
        apiVersion: v1
        kind: Service
        metadata:
        name: prod-ml-predict-lb
        labels:
            app: prod-ml-predict
        namespace: prod-ml-app
        spec:
        type: LoadBalancer
        ports:
        - port: 5000
            targetPort: 5000
        selector:
            app: prod-ml-predict

    $kubectl apply -f py-flask-ml-carbon-api/py-flask-ml-carbon.yaml
        # namespace/prod-ml-app created
        # replicationcontroller/prod-ml-predict-rc created
        # service/prod-ml-predict-lb created
            # a replication controller, 
            # a load-balancer service 
            # and a namespace for all of these components
    $kubectl get all --namespace prod-ml-app
        # NAME                           READY   STATUS    RESTARTS   AGE
        # pod/prod-ml-predict-rc-jhr2j   1/1     Running   0          43m
        # pod/prod-ml-predict-rc-vnx28   1/1     Running   0          43m
        # NAME                                       DESIRED   CURRENT   READY   AGE
        # replicationcontroller/prod-ml-predict-rc   2         2         2       43m
        # NAME                         TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
        # service/prod-ml-predict-lb   LoadBalancer   10.103.12.35   <pending>     5000:30437/TCP   43m
    $minikube service list
    #|-------------|----------------------|-----------------------------|
    #|  NAMESPACE  |         NAME         |             URL             |
    #|-------------|----------------------|-----------------------------|
    #| default     | kubernetes           | No node port                |
    #| kube-system | default-http-backend | http://192.168.99.106:30001 |
    #| kube-system | kube-dns             | No node port                |
    #| kube-system | kubernetes-dashboard | No node port                |
    #| prod-ml-app | prod-ml-predict-lb   | http://192.168.99.106:30437 |
    #|-------------|----------------------|-----------------------------|
    #prod -> 
        $curl http://192.168.99.106:31145/carbon/v1/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
    #canary -> 
        $curl http://192.168.99.106:31720/carbon/v1/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'

    # set our new namespace as the default context
        kubectl config set-context $(kubectl config current-context) --namespace=prod-ml-app
            kubectl config get-contexts
            CURRENT   NAME                  CLUSTER               AUTHINFO              NAMESPACE
    *       minikube              minikube              minikube                        prod-ml-app
            staging.zdevops.xyz   staging.zdevops.xyz   staging.zdevops.xyz 
            kubectl get all
    # switch back to the default namespace    
        kubectl config set-context $(kubectl config current-context) --namespace=default
            kubectl config get-contexts
            CURRENT   NAME                  CLUSTER               AUTHINFO              NAMESPACE
    *       minikube              minikube              minikube                        default
            staging.zdevops.xyz   staging.zdevops.xyz   staging.zdevops.xyz
    # tear-down this application
    $ kubectl delete -f py-flask-ml-carbon-api/py-flask-ml-carbon.yaml
        # namespace "prod-ml-app" deleted
        # replicationcontroller "prod-ml-predict-rc" deleted
        # service "prod-ml-predict-lb" deleted                
## Why Helm Charts added to the project?
    # Helm - a framework for creating, executing and managing Kubernetes deployment templates.
    # Seldon-Core can also be deployed using Helm
    ########################################################
    # Why Seldon Core deployment
    # https://github.com/SeldonIO/seldon-core
    ########################################################    
        1) open source platform for deploying machine learning models on a Kubernetes cluster.
        2) metrics and ensure proper governance and compliance for your running machine learning models
        3) out of the box best-practices for logging, tracing and base metrics
        4) support for deployment strategies such as running A/B test and canaries
        5) inferences graphs for microservice-based serving strategies such as multi-armed bandits or pre-processing
        Because I had only 3 weeks for the project implementation, I had no time to deploy ML model using Seldon Core deployment, using Helm. This is project stretch goal and can be implemented to have better k8 cluster monitoring and tracing. But I did implemented Helm charts for load deployments.
## Helm Charts to define and deploy Carbon ML Model - predict service
    # Installing Helm
        $brew install kubernetes-helm
    # Helm relies on a dedicated deployment server, referred to as the ‘Tiller’, 
    # to be running within the same Kubernetes cluster 
    # Before we deploy Tiller we need to create a cluster-wide super-user role to assign to it 
    # (via a dedicated service account)
        $kubectl --namespace kube-system create serviceaccount tiller
            serviceaccount/tiller created
        $kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller    
            clusterrolebinding.rbac.authorization.k8s.io/tiller created
    # deploy the Helm Tiller to your Kubernetes cluster
        $helm init --service-account tiller
            # Creating /Users/bird5555/.helm 
            # Creating /Users/bird5555/.helm/repository 
            # Creating /Users/bird5555/.helm/repository/cache 
            # Creating /Users/bird5555/.helm/repository/local 
            # Creating /Users/bird5555/.helm/plugins 
            # Creating /Users/bird5555/.helm/starters 
            # Creating /Users/bird5555/.helm/cache/archive 
            # Creating /Users/bird5555/.helm/repository/repositories.yaml 
            
            Adding stable repo with URL: https://kubernetes-charts.storage.googleapis.com 
            Adding local repo with URL: http://127.0.0.1:8879/charts 
            
            $HELM_HOME has been configured at /Users/bird5555/.helm.
            # Tiller (the Helm server-side component) has been installed into your Kubernetes Cluster.
            # Please note: by default, Tiller is deployed with an insecure 'allow unauthenticated users' # policy.
            # To prevent this, run `helm init` with the --tiller-tls-verify flag.
            # For more information on securing your installation see: https://docs.helm.sh/using_helm/securing-your-helm-installation
    # To initiate a new deployment - referred to as a ‘chart’ in Helm terminology 
        $helm create helm-ml-carbon-predict-app 
            # Creating helm-ml-carbon-predict-app  
            # helm-ml-carbon-predict-app/
            #    | -- charts/
            #    | -- templates/
            #    | Chart.yaml
            #    | values.yaml        
                # charts directory contains other charts that our new chart will depend on 
                # the templates directory contains our Helm templates
                # Chart.yaml contains core information for our chart (e.g. name and version information)
                # values.yaml contains default values to render our templates with, in the case that no 
                # values are passed from the command line
            # To test and examine the rendered template, without having to attempt a deployment
                $minikube start --memory 4096   
                $kubectl config use-context minikube
                $kubectl cluster-info
                $kubectl config use-context minikube
                $minikube service list
                $kubectl get all --namespace prod-ml-app
                $kubectl get all --namespace canary-ml-app
                $kubectl delete -f py-flask-ml-carbon-api/py-flask-ml-carbon.yaml
                $kubectl delete -f py-flask-ml-carbon-api/py-flask-ml-carbon-canary.yaml
                1) create charts
                    $helm create helm-ml-carbon-predict-app
                    $helm create helm-ml-carbon-canary-predict-app
                2) add pod.yaml and service.yaml to templates    
                3) test and examine the rendered template, without having to attempt a deployment   
                    $helm install helm-ml-carbon-predict-app --debug --dry-run
                    # validate extra
                        $helm lint helm-ml-carbon-predict-app
                    $helm install helm-ml-carbon-canary-predict-app --debug --dry-run
                4) execute the deployment and generate a release from the chart
                    $helm install helm-ml-carbon-predict-app
                    $helm install helm-ml-carbon-canary-predict-app
                        ------------------
                        # ignorant-blackbird  - production
                        # smelly-hyena        - canary
                        ------------------
                        # name that Helm has ascribed to it -> XXXXXXXX-yak
                            # NAME:   ignorant-blackbird
                            # LAST DEPLOYED: Tue Jun 25 14:11:57 2019
                            # NAMESPACE: default
                            # STATUS: DEPLOYED
                            # RESOURCES:
                            # ==> v1/Namespace
                            # NAME         STATUS  AGE
                            # prod-ml-app  Active  0s
                            # ==> v1/Pod(related)
                            # NAME                      READY  STATUS             RESTARTS  AGE
                            # prod-ml-predict-rc-wnfhv  0/1    ContainerCreating  0         0s
                            # prod-ml-predict-rc-wvzml  0/1    ContainerCreating  0         0s
                            # ==> v1/ReplicationController
                            # NAME                DESIRED  CURRENT  READY  AGE
                            # prod-ml-predict-rc  2        2        0      0s
                            # ==> v1/Service
                            # NAME                TYPE          CLUSTER-IP    EXTERNAL-IP  PORT(S)         AGE
                            # prod-ml-predict-lb  LoadBalancer  10.107.63.74  <pending>    5000:30765/TCP  0s                                
                5) list all available Helm releases and their names
                    $helm list
                6) status of all their constituent components (e.g. pods, replication controllers, service)
                    $helm status ignorant-blackbird
                    $helm status smelly-hyena
                        # LAST DEPLOYED: Tue Jun 25 14:11:57 2019
                        # NAMESPACE: default
                        # STATUS: DEPLOYED
                        # RESOURCES:
                        # ==> v1/Namespace
                        # NAME         STATUS  AGE
                        # prod-ml-app  Active  2m46s
                        # ==> v1/Pod(related)
                        # NAME                      READY  STATUS   RESTARTS  AGE
                        # prod-ml-predict-rc-wnfhv  1/1    Running  0         2m46s
                        # prod-ml-predict-rc-wvzml  1/1    Running  0         2m46s
                        # ==> v1/ReplicationController
                        # NAME                DESIRED  CURRENT  READY  AGE
                        # prod-ml-predict-rc  2        2        2      2m46s
                        # ==> v1/Service
                        # NAME                TYPE          CLUSTER-IP    EXTERNAL-IP  PORT(S)         AGE
                        # prod-ml-predict-lb  LoadBalancer  10.107.63.74  <pending>    5000:30765/TCP  2m46s
                7) versioning and scaling
                    exhaling-whippet
                    mottled-marsupial   
                        $helm upgrade --set scale=4, tag="2" exhaling-whippet ./helm-ml-carbon-predict-app     
                8) $delete charts deployment
                    $helm delete ignorant-blackbird 
                    $helm delete smelly-hyena 
                9) $minikube service list  
                    #|-------------|----------------------|-----------------------------|
                    #|  NAMESPACE  |         NAME         |             URL             |
                    #|-------------|----------------------|-----------------------------|
                    #| default     | kubernetes           | No node port                |
                    #| kube-system | default-http-backend | http://192.168.99.107:30001 |
                    #| kube-system | kube-dns             | No node port                |
                    #| kube-system | kubernetes-dashboard | No node port                |
                    #| kube-system | tiller-deploy        | No node port                |
                    #| prod-ml-app | prod-ml-predict-lb   | http://192.168.99.107:30765 |
                    #| canary-ml-ap| canary-ml-predict-lb | http://192.168.99.107:32296 |
                    #|-------------|----------------------|-----------------------------| 
                    #Production  
                        $curl http://192.168.99.107:30765/carbon/v1/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
                    #Canary
                        $curl http://192.168.99.107:32296/carbon/v3/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
