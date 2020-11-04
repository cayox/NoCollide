# download python 3.8.5
wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz
# unpack it
tar xf Python-3.8.5.tgz
# install necessary libraries
sudo apt install libssl-dev
sudo apt install libffi-dev
# delete tarball
rm -r Python-3.8.5.tgz
# move into python dir 
cd ./Python-3.8.5
# configure python
./configure
# create installation file 
make -j -l 4
# install file 
sudo make altinstall
# if you want to set python 3.8.5 as default python uncomment the next lines:

# echo "alias python=python3.8" >> ~/.bashrc
# echo "alias pip=pip3.8" >> ~/.bashrc
# source ~/.bashrc

echo you can use python 3.8.5 by typing "python3.8" instead of regular "python" command
