from flask import Blueprint, render_template

view = Blueprint('view', __name__)


@view.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@view.route('/', methods=['GET', 'POST'])
@view.route('/order', methods=['GET', 'POST'])
def order():
    return render_template('order.html')


@view.route('/order_check', methods=['GET', 'POST'])
def order_check():
    return render_template('order_check.html')


@view.route('/order_complete', methods=['GET', 'POST'])
def order_complete():
    return render_template('order_complete.html')


@view.route('/order_status', methods=['GET', 'POST'])
def order_status():
    return render_template('order_status.html')


@view.route('/kitchen', methods=['GET', 'POST'])
def kitchen():
    return render_template('kitchen.html')
