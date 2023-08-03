MANAGEPATH="/mdfsvc/ManagePlatform"
PYTHONPATH=$PYTHONPATH:$MANAGEPATH

export PYTHONPATH

nohup python3 ${MANAGEPATH}/manage.py runserver > /dev/null 2>&1 &
