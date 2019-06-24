#!/bin/bash
echo " ********************************************************"
echo " **************** Canary deployment to AWS **************"
echo " ********************************************************"
cd /Users/bird5555/Desktop/Vagrant/devops-box/projects/aws-ops-insight/carbon_kubeflow
export NAME=$(terraform output cluster_name)
echo $NAME
export KOPS_STATE_STORE=$(terraform output state_store)
echo $KOPS_STATE_STORE
export ZONES=us-west-2a,us-west-2b,us-west-2c
echo $ZONES
echo "validate k8 aws cluster"
kubectl config use-context staging.zdevops.xyz
sleep 3
kops validate cluster --state=$(terraform output state_store)
sleep 10
kubectl get all --namespace canary-ml-app
    # NAME                             READY   STATUS    RESTARTS   AGE
    # pod/canary-ml-predict-rc-gf6h8   1/1     Running   0          59m
    # pod/canary-ml-predict-rc-rxcvt   1/1     Running   0          59m
    # NAME                                         DESIRED   CURRENT   READY   AGE
    # replicationcontroller/canary-ml-predict-rc   2         2         2       59m
    # NAME                           TYPE           CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)          AGE
    # service/canary-ml-predict-lb   LoadBalancer   100.68.31.164   ae38f496396c111e9a22102f6ab83b2c-1257448687.us-west-2.elb.amazonaws.com   5000:30207/TCP   59mecho "canary clean k8 deployments"
kubectl delete -f food_facts/py-flask-ml-carbon-api/py-flask-ml-carbon-canary.yaml
sleep 30
echo "apply canary deployments ver. ${API_VERSION}"
kubectl apply -f food_facts/py-flask-ml-carbon-api/py-flask-ml-carbon-canary.yaml
    # namespace/canary-ml-app created
    # replicationcontroller/canary-ml-predict-rc created
    # service/canary-ml-predict-lb created
sleep 40
# ******************************
# production deployment
# ******************************
# ******************************
# canary deployment
# ******************************
# replicationcontroller/canary-ml-predict-rc   2         2         2       59m
# NAME                           TYPE           CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)          AGE
# service/canary-ml-predict-lb   LoadBalancer   100.68.31.164   ae38f496396c111e9a22102f6ab83b2c-1257448687.us-west-2.elb.amazonaws.com   5000:30207/TCP   59mecho "canary clean k8 deployments"
#curl http://ae38f496396c111e9a22102f6ab83b2c-1257448687.us-west-2.elb.amazonaws.com:5000/carbon/v3/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
# {
#   "prediction,v3": [
#     318.3333333333333
#   ]
# }
