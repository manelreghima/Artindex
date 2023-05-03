# Art Index

## Install Streamlit

Streamlit requires Python 3.8 (3.9 appears not yet to be supported)

$ virtualenv -p /usr/bin/python3.8 venv

$ source venv/bin/activate

$ pip install streamlit

## Install Requirements - Streamlit Standalone

$ git pull https://github.com/kanvas-ai/artindex.git

$ pip install -r requiments.txt

$ streamlit run Home.py

This should launch a browser on localhost:8501.


## Update Content - Streamlit + Ngnix

### Update Code
$ cd artindex
$ git pull https://github.com/kanvas-ai/artindex.git

### Reload Ngnix / Streamlit
```
$ sudo systemctl daemon-reload
$ sudo systemctl stop artindex
$ sudo systemctl disable artindex
$ sudo systemctl start artindex
$ sudo systemctl enable artindex
$ sudo systemctl status artindex
```

### New Files

* Navigate to /etc/systemd/system directory
* Open corresponding service file. In our case artindex.service
* Under [Service] change the field ExecStart .py extension file name. For example: ExecStart=sudo python3.10 -m streamlit run English.py
