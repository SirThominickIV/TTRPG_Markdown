cd $home
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
curl -O https://www.python.org/ftp/python/3.14.3/Python-3.14.3.tar.xz
tar -xf Python-3.14.3.tar.xz
rm Python-3.14.3.tar.xz
cd Python-3.14.3
./configure --enable-optimizations
make -j 4
sudo make altinstall
