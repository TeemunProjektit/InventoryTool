from flask import Flask

# Special variable, determines the location for Flask-object.
app = Flask(__name__)
# Load configurations from configuration file, not included in git.
app.config.from_pyfile('config.conf', silent=True)

from app import views
