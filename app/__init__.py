from flask import Flask, Blueprint
from flask_restx import Api
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

bp = Blueprint('api', __name__, url_prefix='/sponsor/api')
api = Api(bp)

app.register_blueprint(bp)
from app import routes
from app import api_routes
