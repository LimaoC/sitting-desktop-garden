#!/bin/bash
sudo swapoff /var/swap 
sudo fallocate -l 2G /var/swap 
sudo mkswap /var/swap 
sudo swapon /var/swap 