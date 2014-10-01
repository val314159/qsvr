source .v/bin/activate
run_qsvr () { python -u qsvr.py; }
run () { python -u qsvr.py; }
launch_qsvr () { python -u qsvr.py 1>LOG 2>&1 &}
launch () { python -u qsvr.py 1>LOG 2>&1 &}
unlaunch () { killall -9 python; }
cln () { rm -fr .? *.pyc *~ 2>/dev/null; }
$*
