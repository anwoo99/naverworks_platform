NAVERWORKSPATH="/mdfsvc/NaverWorks"
PYTHONPATH=$PYTHONPATH:$NAVERWORKSPATH

export PYTHONPATH

nohup python3 ${NAVERWORKSPATH}/manage.py runserver > /dev/null 2>&1 &
