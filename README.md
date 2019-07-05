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
