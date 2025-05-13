from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    total = db.Column(db.Integer, nullable=False)
    completado = db.Column(db.Boolean, default=False)
    items = db.relationship('ItemPedido', backref='pedido', lazy=True)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    subtotal = db.Column(db.Integer)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
