#!/bin/bash 

if [[ -f requirements.txt ]]; then 
	~/.FaceSwap/venv/FaceSwap/bin/pip install -r requirements.txt || exit 1
else
	exit 1
fi


