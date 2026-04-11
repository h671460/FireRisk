#!/bin/bash

echo "Applying namespace..."
kubectl apply -f namespace.yaml

echo "Applying postgres..."
kubectl apply -f postgres/configmap.yaml
kubectl apply -f postgres/secret.yaml
kubectl apply -f postgres/service.yaml
kubectl apply -f postgres/statefulset.yaml

echo "Waiting for postgres to be ready..."
kubectl wait --for=condition=ready pod/postgres-0 -n group02 --timeout=120s

echo "Applying keycloak..."
kubectl apply -f keycloak/configmap.yaml
kubectl apply -f keycloak/secret.yaml
kubectl apply -f keycloak/service.yaml
kubectl apply -f keycloak/deployment.yaml

echo "Waiting for keycloak to be ready..."
kubectl wait --for=condition=ready pod -l app=keycloak -n group02 --timeout=180s

echo "Applying ingress..."
kubectl apply -f ingress.yaml

echo "All done! Starting port-forward..."
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 80:80