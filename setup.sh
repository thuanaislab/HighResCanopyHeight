python -m pip install virtualenv
python -m virtualenv hrch-env
source hrch-env/bin/activate

pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu117
pip install -r requirements.txt

deactivate