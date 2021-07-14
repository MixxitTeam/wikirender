#!/usr/bin/bash

export PYTHONUNBUFFERED=on
php renderall.php $@ 2>&1 > /dev/null
