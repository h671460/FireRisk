#!/bin/bash

set -e

echo "Applying namespace..."
kubectl apply -f namespace.yaml

echo "Applying postgres..."
kubectl apply -f postgres/configmap.yaml
kubectl apply -f postgres/secret.yaml
kubectl apply -f postgres/statefulset.yaml

# only recreate service if clusterIP is None (headless)
POSTGRES_CLUSTER_IP=$(kubectl get svc postgres -n group02 -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
if [ "$POSTGRES_CLUSTER_IP" = "None" ] || [ -z "$POSTGRES_CLUSTER_IP" ]; then
  echo "Recreating postgres service..."
  kubectl delete service postgres -n group02 --ignore-not-found
  kubectl apply -f postgres/service.yaml
else
  kubectl apply -f postgres/service.yaml
fi

echo "Waiting for postgres to be ready..."
kubectl wait --for=condition=ready pod/postgres-0 -n group02 --timeout=120s

echo "Applying timescaledb..."
kubectl apply -f timescaledb/configmap.yaml
kubectl apply -f timescaledb/configmap-init.yaml
kubectl apply -f timescaledb/secret.yaml
kubectl apply -f timescaledb/service.yaml
kubectl apply -f timescaledb/statefulset.yaml

echo "Waiting for timescaledb to be ready..."
kubectl wait --for=condition=ready pod/timescaledb-0 -n group02 --timeout=120s

echo "Applying keycloak..."
kubectl apply -f keycloak/configmap.yaml
kubectl apply -f keycloak/secret.yaml
kubectl apply -f keycloak/service.yaml
kubectl apply -f keycloak/deployment.yaml

echo "Waiting for keycloak to be ready..."
kubectl wait --for=condition=ready pod -l app=keycloak -n group02 --timeout=180s

echo "Applying frcm-api..."
kubectl apply -f frcm-api/configmap.yaml
kubectl apply -f frcm-api/secret.yaml
kubectl apply -f frcm-api/service.yaml
kubectl apply -f frcm-api/deployment.yaml

echo "Waiting for frcm-api to be ready..."
kubectl wait --for=condition=ready pod -l app=frcm-api -n group02 --timeout=120s

echo "Applying ingress..."
kubectl apply -f ingress.yaml

echo "All done! Starting port-forward..."
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 80:80