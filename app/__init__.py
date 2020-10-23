from flask import Flask
from flask_restx import Api
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)
from app import routes
from app import api_routes
