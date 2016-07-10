from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ubuntu/testFlaskJSON/testFlask.db'
db = SQLAlchemy(app)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), unique=True)
    created_date = db.Column(db.DateTime, )
    runtime = db.Column(db.Float)
    usedGPU = db.Column(db.Boolean)

    def __init__(self, filename, runtime, usedGPU, mapSize):
        self.filename = filename
        self.runtime = runtime
        self.usedGPU = usedGPU
        self.mapSize = mapSize
        self.created_date = datetime.utcnow()
        

    def __repr__(self):
        return '<Upload %r>' % self.filename
