source venv/bin/activate
echo "Activated virtual env"
export FLASK_APP=rentals_app/
export FLASK_ENV=development
flask run --port 5000
