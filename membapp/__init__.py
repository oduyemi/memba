from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__,instance_relative_config=True)

#load the config
app.config.from_pyfile('config.py', silent=False)

db = SQLAlchemy(app)
#load the routes

from membapp import adminroutes,userroutes