#!/usr/bin/env bash

WORK_DIR=/src/

if coverage run $WORK_DIR/manage.py test prescription; then
  echo 'Test Passed!!'
else
	echo 'Tests Failed'
	exit 1
fi

if python $WORK_DIR/manage.py migrate --no-input; then
  echo 'Migrations executed!!'
else
	echo 'Error migration'
	exit 1
fi

if python $WORK_DIR/manage.py collectstatic --no-input; then
  echo 'Static Configured!!'
else
	echo 'Error Configure Static :/'
	exit 1
fi

echo 'Coverage Report....'
coverage report

python $WORK_DIR/manage.py runserver 0.0.0.0:8000