sudo swapoff /swapfile 
sudo fallocate -l 2G /swapfile 
sudo mkswap /swapfile 
sudo swapon /swapfile 