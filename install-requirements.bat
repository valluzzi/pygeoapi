@echo off
:: c:\Python311\python -m venv venv
:: .\venv\Scripts\activate
python -m pip install -U pip
pip install .\GDAL-3.4.3-cp311-cp311-win_amd64.whl
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install kubernetes