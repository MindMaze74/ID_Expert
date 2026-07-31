#!/bin/bash
BASTION_IP=$1
PRIVATE_KEY=$2
if [ -z "$BASTION_IP" ] || [ -z "$PRIVATE_KEY" ]; then
  echo "Usage: $0 <bastion_ip> <private_key_path>"
  exit 1
fi
ssh -L 3000:10.0.2.10:3000 -N -f -i $PRIVATE_KEY ubuntu@$BASTION_IP
echo "Tunnel established. Grafana available at http://localhost:3000"
