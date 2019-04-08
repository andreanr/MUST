from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ay-mama'

from app import routes
