from faucet import db
import datetime

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reqtime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reqamt = db.Column(db.Integer)
    address = db.Column(db.String())
