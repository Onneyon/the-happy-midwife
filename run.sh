#!/usr/bin/zsh
export GOOGLE_APPLICATION_CREDENTIALS='/home/alex/gcp-app/thehappymidwife-2e3febc76e43.json'
FLASK_ENV=development FLASK_APP="main.py" python -m flask run --host=0.0.0.0 --port=5000 

