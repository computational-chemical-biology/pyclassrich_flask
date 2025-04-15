export PATH=$PATH:/usr/lib/jvm/default-java/bin/
wget https://raw.githubusercontent.com/computational-chemical-biology/ChemWalker/refs/heads/master/bin/network_walk
#wget https://github.com/computational-chemical-biology/ChemWalker/blob/master/bin/MetFrag2.3-CL.jar
sed -i '3d' network_walk
sed -i '3d' network_walk
sed -i '9d' network_walk
#conda install -n pyclassrich -c conda-forge rdkit -y
ln -s /opt/conda/envs/pyclassrich/lib/python3.7/site-packages/rdkit/ /opt/conda/envs/chemwalker/lib/python3.8/site-packages/rdkit
apt install -y default-jre

