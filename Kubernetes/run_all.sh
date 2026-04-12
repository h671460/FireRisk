#!/bin/bash

set -e

echo "================================================"
echo "Deploying FireRisk to Kubernetes namespace: group02"
echo "================================================"

echo ""
echo "Applying namespace..."
kubectl apply -f namespace.yaml

echo ""
echo "Applying postgres..."
kubectl apply -f postgres/configmap.yaml
kubectl apply -f postgres/secret.yaml
kubectl apply -f postgres/service.yaml
kubectl apply -f postgres/statefulset.yaml
echo "Waiting for postgres to be ready..."
kubectl wait --for=condition=ready pod/postgres-0 -n group02 --timeout=120s
echo "Postgres is ready!"

echo ""
echo "Applying timescaledb..."
kubectl apply -f timescaledb/configmap.yaml
kubectl apply -f timescaledb/configmap-init.yaml
kubectl apply -f timescaledb/secret.yaml
kubectl apply -f timescaledb/service.yaml
kubectl apply -f timescaledb/statefulset.yaml
echo "Waiting for timescaledb to be ready..."
kubectl wait --for=condition=ready pod/timescaledb-0 -n group02 --timeout=120s
echo "Timescaledb is ready!"

echo ""
echo "Applying keycloak..."
kubectl apply -f keycloak/configmap.yaml
kubectl apply -f keycloak/secret.yaml
kubectl apply -f keycloak/service.yaml
kubectl apply -f keycloak/deployment.yaml
echo "Waiting for keycloak to be ready..."
kubectl wait --for=condition=ready pod -l app=keycloak -n group02 --timeout=180s
echo "Keycloak is ready!"

echo ""
echo "Applying frcm-api..."
kubectl apply -f frcm-api/configmap.yaml
kubectl apply -f frcm-api/secret.yaml
kubectl apply -f frcm-api/service.yaml
kubectl apply -f frcm-api/deployment.yaml
echo "Waiting for frcm-api to be ready..."
kubectl wait --for=condition=ready pod -l app=frcm-api -n group02 --timeout=120s
echo "frcm-api is ready!"

echo ""
echo "Applying frontend..."
kubectl apply -f frontend/configmap.yaml
kubectl apply -f frontend/deployment.yaml
kubectl apply -f frontend/service.yaml
echo "Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n group02 --timeout=120s
echo "Frontend is ready!"

echo ""
echo "Applying ingress..."
kubectl apply -f ingress.yaml

echo ""
echo "================================================"
echo "All services are up!"
kubectl get pods -n group02
kubectl get services -n group02
kubectl get ingress -n group02
echo "================================================"

echo ""
echo "Starting port-forward on port 80..."
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 80:80