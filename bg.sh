#!/bin/bash
while true; do
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
sleep 6
done