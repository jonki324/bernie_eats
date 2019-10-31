from flask import Blueprint, render_template, request, session, redirect, url_for
from application.models import db, Item, MasterLoc, MasterStatus, Order, OrderStatus, OrderStatusHistory

view = Blueprint('view', __name__)


waiting = 1
cooking = 2
carrying = 3
cancelled = 4
completed = 5

@view.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@view.route('/', methods=['GET', 'POST'])
@view.route('/order', methods=['GET', 'POST'])
def order():
    items = db.session.query(Item).all()
    locs = db.session.query(MasterLoc).all()

    forms = []
    for i in items:
        form = {
            'name': 'odr_cnt_{}'.format(i.id),
            'val': session.get('odr_cnt_{}'.format(i.id), default=0)
        }
        forms.append(form)
    loc_id = session.get('loc_id', default=1)

    if request.method == 'POST':
        session['loc_id'] = request.form['loc_id']
        for i in items:
            session['odr_cnt_{}'.format(i.id)] = request.form['odr_cnt_{}'.format(i.id)]
        return redirect(url_for('view.order_check'))

    return render_template('order.html', items=zip(items, forms), locs=locs, loc_id=loc_id)


@view.route('/order_check', methods=['GET', 'POST'])
def order_check():
    items = db.session.query(Item).all()
    odr = get_ord_cnt_from_session(items)

    loc = db.session.query(MasterLoc).filter(MasterLoc.id == odr['loc_id']).first()

    forms = []
    total = 0
    for i in items:
        form = {
            'name': i.name,
            'cnt': odr['odr_cnt_{}'.format(i.id)],
            'price': int(odr['odr_cnt_{}'.format(i.id)]) * i.price,
        }
        total += form['price']
        forms.append(form)

    if request.method == 'POST':
        loc = db.session.query(MasterLoc).filter(MasterLoc.id == odr['loc_id']).first()
        master_status = db.session.query(MasterStatus).filter(MasterStatus.id == waiting).first()
        order_status = OrderStatus(status=master_status)
        order_status_history = OrderStatusHistory(status=master_status)
        order = Order(count_buta=odr['odr_cnt_1'],
                      count_modern=odr['odr_cnt_2'],
                      loc=loc,
                      status=order_status,
                      status_history=order_status_history)

        db.session.add(order)
        db.session.commit()

        return redirect(url_for('view.order_complete'))

    return render_template('order_check.html', forms=forms, loc=loc, total=total)


@view.route('/order_complete', methods=['GET', 'POST'])
def order_complete():
    return render_template('order_complete.html')


@view.route('/order_status', methods=['GET', 'POST'])
def order_status():
    return render_template('order_status.html')


@view.route('/kitchen', methods=['GET', 'POST'])
def kitchen():
    return render_template('kitchen.html')


def get_ord_cnt_from_session(items):
    forms = {}
    for i in items:
        forms['odr_cnt_{}'.format(i.id)] = session.get('odr_cnt_{}'.format(i.id), default=0)
    forms['loc_id'] = session.get('loc_id', default=1)
    return forms
