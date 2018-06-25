#!/bin/bash

# Create dir for environment

cd ~/.FaceSwap && mkdir venv && cd venv 

# Create environment 

virtualenv --no-site-packages --python=/usr/bin/python2.7 FaceSwap
