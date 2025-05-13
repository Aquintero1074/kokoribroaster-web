from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

from models import db, Usuario, Pedido, ItemPedido

app = Flask(__name__)
app.secret_key = 'kokori-secreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kokoribroaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

menu = {
    1: {"nombre": "Pollo broaster combo", "precio": 25000},
    2: {"nombre": "Pollo frito combo", "precio": 24000},
    3: {"nombre": "Papas fritas", "precio": 8000},
    4: {"nombre": "Gaseosa 400ml", "precio": 3000},
    5: {"nombre": "Agua", "precio": 2000}
}

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.before_first_request
def initialize():
    with app.app_context():
        db.create_all()


@app.route('/')
@login_required
def index():
    return render_template('index.html', menu=menu)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if Usuario.query.filter_by(username=username).first():
            flash("Usuario ya existe")
            return redirect(url_for('register'))
        new_user = Usuario(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registro exitoso. Inicia sesión.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash("Credenciales inválidas.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/hacer_pedido', methods=['POST'])
@login_required
def hacer_pedido():
    total = 0
    items = []
    for id_str in menu:
        cantidad = int(request.form.get(f"producto_{id_str}", 0))
        if cantidad > 0:
            item_info = menu[id_str]
            subtotal = cantidad * item_info['precio']
            items.append(ItemPedido(nombre=item_info['nombre'], cantidad=cantidad, subtotal=subtotal))
            total += subtotal
    if items:
        nuevo_pedido = Pedido(user_id=current_user.id, total=total)
        db.session.add(nuevo_pedido)
        db.session.commit()
        for item in items:
            item.pedido_id = nuevo_pedido.id
            db.session.add(item)
        db.session.commit()
        flash("Pedido registrado correctamente.")
    return redirect(url_for('ver_pedidos'))

@app.route('/pedidos')
@login_required
def ver_pedidos():
    pedidos = Pedido.query.filter_by(user_id=current_user.id).all()
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/completar/<int:pid>')
@login_required
def completar_pedido(pid):
    pedido = Pedido.query.get(pid)
    if pedido and pedido.user_id == current_user.id:
        pedido.completado = True
        db.session.commit()
    return redirect(url_for('ver_pedidos'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)