#!/bin/bash

echo "install python2.7 interpreter"

if [[ -z $(dpkg --get-selections | egrep "python2.7\s") ]]; then 
	bash InstallPython.sh || ( echo "Python2.7 doesn't install. Error!" && exit 0 )
fi

echo "install pip for python2.7"

if [[ -z $(dpkg --get-selections | egrep "python-pip\s") ]]; then 
	bash InstallPythonPip.sh || ( echo "Pip doesn't install. Error!" && exit 0 )
fi

echo "install virtualenv" 

if [[ -z $(dpkg --get-selections | egrep "virtualenv\s") ]]; then 
        bash InstallVirtualenv.sh || ( echo "Virtualenv doesn't install. Error!" && exit 0 )
fi

echo "install python boost"

if [[ -z $(dpkg --get-selections | egrep "boost-python-dev\s") ]]; then
	bash InstallPythonBoost.sh || ( echo "Python boost doesn't install. Error!" && exit 0 )
fi

echo "install cmake"

if [[ -z $(dpkg --get-selections | egrep "cmake\s") ]]; then
        bash InstallCmake.sh || ( echo "Cmake doesn't install. Error!" && exit 0 )
fi


echo "Create FaceSwap dir"

if [[ -d ~/.FaceSwap/ ]]; then
	rm -rf ~/.FaceSwap/
fi

mkdir ~/.FaceSwap || exit 0

echo "Create Virtial environment"

bash CreateVirtualenv.sh 

echo "Pip install requirements"

bash PipInstallReq.sh || ( echo "Pip doesn't install requirements!"; exit 0 )

echo "Project is ready"
