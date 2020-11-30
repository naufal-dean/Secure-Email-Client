echo "[+] Adding PYTHONPATH..."
export PYTHONPATH=`pwd`:$PYTHONPATH
echo "[+] Starting webpymail server..."
cd webpymail
python3 manage.py runserver
cd ..
echo "[+] Server closed..."
