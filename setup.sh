#!bin/bash/

echo "Creting the environment to run the code"
if conda create -n envSP python=3.6 numpy scipy tqdm ; then
    echo "Environment envSP successfuly created"
    if source activate envSP ; then
        echo "Installing matplotlib"
        if conda install -c conda-forge matplotlib ; then
            echo "Matplotlib successfuly installed"
            if pip install opencv-python ; then
                echo "OpenCV successfuly installed"
                echo "Everything was installed!"
                echo "You can start running the code using the command python run.py --video nameofvideo --json 0"
            else
                echo "OpenCV couldn't be installed. Abort"
            fi
        else
            echo "Matplotlib couldn't be installed. Abort"
        fi
    else
        echo "Couldn't activate the environment. Please check that it is indeed created. Abort"
    fi
else
    echo "The environment couldn't be created. Abort"
fi
