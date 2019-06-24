#!/bin/bash
echo " *************************************************"
echo " **************** Canary deployment **************"
echo " *************************************************"
sleep 3
cd /Users/bird5555/Desktop/Vagrant/devops-box/projects/aws-ops-insight/carbon_kubeflow/food_facts
# --------------------------------------------------------------------
# SET API VERSION HERE FOR DEPLOYMENT
# --------------------------------------------------------------------
export API_VERSION=3
echo "build docker-image with flask ver. ${API_VERSION}"
# docker build . -t bird5555/carbon-api-canary:${API_VERSION} --build-arg API_VERSION=${API_VERSION}
docker build . -t bird5555/carbon-api-canary --build-arg API_VERSION=${API_VERSION}
docker rm -f carbon-api-canary
# docker run -d --name carbon-api-canary -p 5000:5000 bird5555/carbon-api-canary:${API_VERSION}
docker run -d --name carbon-api-canary -p 5000:5000 bird5555/carbon-api-canary
sleep 3
docker logs carbon-api-canary
docker rm -f carbon-api-canary
# docker push bird5555/carbon-api-canary:${API_VERSION}
docker push bird5555/carbon-api-canary
sleep 3
echo "set minikube context"
kubectl config use-context minikube
echo "canary clean k8 deployments"
sleep 3
# kubectl delete -f py-flask-ml-carbon-api/py-flask-ml-carbon.yaml
# sleep 3
kubectl delete -f py-flask-ml-carbon-api/py-flask-ml-carbon-canary.yaml
sleep 10
echo "apply canary deployments ver. ${API_VERSION}"
kubectl apply -f py-flask-ml-carbon-api/py-flask-ml-carbon-canary.yaml
sleep 10
kubectl cluster-info
kubectl get all --namespace canary-ml-app
minikube service list
sleep 10
# ******************************
# production deployment
# ******************************
#curl http://192.168.99.106:30059/carbon/v1/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
# {
#   "prediction,v1": [
#     318.3333333333333
#   ]
# }
# ******************************
# canary deployment
# ******************************
#curl http://192.168.99.106:31822/carbon/v3/predict --request POST --header "Content-Type: application/json" --data '{"prediction": [2077.0,0,23.0,11.0,0,0,0,0,0,0,0,0,0,0,63.0,28.0,0,0,0,4.5,7.0,0.93,0.366141732283465,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}'
# {
#   "prediction,v3": [
#     318.3333333333333
#   ]
# }

