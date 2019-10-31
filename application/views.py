from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from application.models import db, Item, MasterLoc, MasterStatus, Order, OrderStatus, OrderStatusHistory

view = Blueprint('view', __name__)

ITEM_ID_BUTA = 1
ITEM_ID_MODERN = 2
WAITING = 1
COOKING = 2
CARRYING = 3
CANCELLED = 4
COMPLETED = 5


@view.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@view.route('/', methods=['GET', 'POST'])
@view.route('/order', methods=['GET', 'POST'])
def order():
    session.pop('order_id', default=None)
    session.pop('loc_name', default=None)

    items = db.session.query(Item).all()
    locs = db.session.query(MasterLoc).all()

    forms = {}
    for i in items:
        forms[i.id] = {
            'name': 'odr_cnt_{}'.format(i.id),
            'val': session.get('odr_cnt_{}'.format(i.id), default=0)
        }
    loc_id = session.get('loc_id', default=1)

    if request.method == 'POST':
        order_form = {'loc_id': request.form['loc_id']}
        tmp_items = {}
        for i in items:
            tmp = {i.id: {'odr_cnt': 0}}
            tmp[i.id]['odr_cnt'] = request.form['odr_cnt_{}'.format(i.id)]
            tmp_items.update(tmp)
        order_form['items'] = tmp_items
        # order_form = {
        #     'loc_id': 1,
        #     'items': {
        #         1(item_id): {
        #             'odr_cnt': 5
        #         },
        #         2(item_id): {
        #             'odr_cnt': 5
        #         }
        #     }
        # }
        session['order_form'] = order_form

        print(order_form)

        return redirect(url_for('view.order_check'))

    return render_template('order.html', items=items, forms=forms, locs=locs, loc_id=loc_id)


@view.route('/order_check', methods=['GET', 'POST'])
def order_check():
    order_form = session.get('order_form', default=None)
    if order_form is None:
        return redirect(url_for('view.order'))

    items = db.session.query(Item).all()
    loc = db.session.query(MasterLoc).filter(MasterLoc.id == order_form['loc_id']).first()

    forms = []
    total = 0
    for i in items:
        name = i.name
        price = i.price
        odr_cnt = int(order_form['items'][str(i.id)]['odr_cnt'])
        subtotal = odr_cnt * i.price
        total += subtotal
        form = {
            'name': name,
            'price': price,
            'odr_cnt': odr_cnt,
            'subtotal': subtotal,
        }
        forms.append(form)

    if request.method == 'POST':
        master_status = db.session.query(MasterStatus).filter(MasterStatus.id == WAITING).first()
        order_status = OrderStatus(status=master_status)
        order_status_history = OrderStatusHistory(status=master_status)
        order = Order(count_buta=order_form['items'][str(ITEM_ID_BUTA)]['odr_cnt'],
                      count_modern=order_form['items'][str(ITEM_ID_MODERN)]['odr_cnt'],
                      loc=loc,
                      status=order_status,
                      status_history=order_status_history)

        db.session.add(order)
        db.session.commit()

        session['order_id'] = order.id
        session['loc_name'] = loc.name
        session.pop('order_form')

        return redirect(url_for('view.order_complete'))

    return render_template('order_check.html', forms=forms, loc=loc, total=total)


@view.route('/order_complete', methods=['GET', 'POST'])
def order_complete():
    order_id = session.get('order_id', default=None)
    loc_name = session.get('loc_name', default=None)

    if order_id is None:
        return redirect(url_for('view.order'))

    return render_template('order_complete.html', order_id=order_id, loc_name=loc_name)


@view.route('/order_status', methods=['GET', 'POST'])
def order_status():
    if request.method == 'POST':
        res = {
            'is_err': True
        }
        order_id = request.form['order_id']
        if order_id:
            order = db.session.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                res = {
                    'is_err': False,
                    'order_id': order_id,
                    'order_stats': order.status.status.name,
                    'is_cancelable': True if order.status.status_id == WAITING else False
                }
        return jsonify(res)

    return render_template('order_status.html')


@view.route('/kitchen', methods=['GET', 'POST'])
def kitchen():
    return render_template('kitchen.html')
