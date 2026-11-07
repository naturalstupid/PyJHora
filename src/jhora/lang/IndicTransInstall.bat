@echo off
set SETUPTOOLS_USE_DISTUTILS=stdlib
python -m pip install --upgrade pip setuptools wheel cython
python -m pip install IndicTransToolkit
pause

python -c "from pip._vendor.truststore import extract_from_ssl; extract_from_ssl(); from huggingface_hub import snapshot_download; snapshot_download('ai4bharat/indictrans2-en-indic-dist-200M', local_dir=r'C:\models\indictrans2-en-indic-dist-200M')"
pause