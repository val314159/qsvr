if [ -e v ];then echo skipping; else virtualenv .v; fi
source env.sh
pip install bottle leveldb gevent
$*