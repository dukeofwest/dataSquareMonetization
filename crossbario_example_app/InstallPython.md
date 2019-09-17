# Install dependencies
```bash
sudo apt-get install libffi-dev openssl-dev libssl1.0-dev python3-openssl
```
# Download and build Python 
```bash
mkdir -p $HOME/Python/
cd $HOME/Python/
wget "https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz"
tar xf Python-3.7.2.tgz
cd Python-3.7.2
./configure --enable-loadable-sqlite-extensions  --prefix=$HOME/Python/Python-3.7.2
make
make install
```
# Set up the path
```bash
cd $HOME/Python/Python-3.7.2/bin
export PATH=$PWD:$PATH
```
# Create a virtual environment
```bash
cd $HOME/Python/
python3.7 -m venv vpy_3.7.2
```

