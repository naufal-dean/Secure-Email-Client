echo "[+] Adding PYTHONPATH..."
export PYTHONPATH=`pwd`:$PYTHONPATH
echo "[+] Run migrate --run-syncdb..."
cd webpymail
python3 manage.py migrate --run-syncdb
cd ..
echo "[+] Initialization done..."
