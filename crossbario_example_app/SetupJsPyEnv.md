#Setup Development Environment for Python and Javascript

## Setup Python
## Building Python version 3.7.2

### Install dependency packages:
```bash
sudo apt install wget build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev uuid-dev
```

### Download and build Python 
```bash
mkdir -p $HOME/Python/
cd $HOME/Python/
wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz
tar xf Python-3.7.2.tgz
cd Python-3.7.2
./configure --enable-loadable-sqlite-extensions  --prefix=$HOME/Python/Python-3.7.2
$make
make install
cd $HOME/Python/Python-3.7.2/bin
export PATH=$PWD:$PATH
```


### Setup virtual environment
```
cd $HOME/Python/
python3.7 -m venv vpy_3.7.2
source vpy_3.7.2/bin/activate
(vpy_3.7.2) code@ubuntu:~$
```


## Setup Javascript
??