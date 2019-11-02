import math
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import login_user, logout_user, login_required
from application.models import db, Item, MasterLoc, MasterStatus, Order, OrderStatus, OrderStatusHistory, User
from application.const import Const
from application.forms import LoginForm


view = Blueprint('view', __name__)


@view.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user, authenticated = User.auth(db.session.query, form.login_id.data, form.password.data)
        if authenticated:
            login_user(user)
            # flash('ログインしました。', 'success')
            return redirect(url_for('view.order'))

        flash('ログインIDかパスワードが違います', 'danger')

    return render_template('login.html', form=form)


@view.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('view.login'))


@view.route('/', methods=['GET', 'POST'])
@view.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    session.pop('order_id', default=None)
    session.pop('loc_name', default=None)

    items = db.session.query(Item).all()
    locs = db.session.query(MasterLoc).all()

    order_form = session.get('order_form', default=None)
    loc_id = 1
    order_form_items = None
    if order_form:
        loc_id = order_form['loc_id']
        order_form_items = order_form['items']

    forms = {}
    for i in items:
        forms[i.id] = {
            'name': 'odr_cnt_{}'.format(i.id),
            'val': order_form_items[str(i.id)]['odr_cnt'] if order_form_items else 0
        }

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

        return redirect(url_for('view.order_check'))

    return render_template('order.html', items=items, forms=forms, locs=locs, loc_id=loc_id)


@view.route('/order_check', methods=['GET', 'POST'])
@login_required
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
        master_status = db.session.query(MasterStatus).filter(MasterStatus.id == Const.WAITING).first()
        order_status = OrderStatus(status=master_status)
        order_status_history = OrderStatusHistory(status=master_status)
        order = Order(count_buta=order_form['items'][str(Const.ITEM_ID_BUTA)]['odr_cnt'],
                      count_modern=order_form['items'][str(Const.ITEM_ID_MODERN)]['odr_cnt'],
                      loc=loc,
                      status=order_status,
                      status_history=order_status_history)

        db.session.add(order)
        db.session.commit()

        # wait_time_m = get_wait_time_m(order.id)

        session['order_id'] = order.id
        session['loc_name'] = loc.name
        # session['wait_time_m'] = wait_time_m

        session.pop('order_form')

        return redirect(url_for('view.order_complete'))

    return render_template('order_check.html', forms=forms, loc=loc, total=total)


@view.route('/order_complete')
@login_required
def order_complete():
    order_id = session.get('order_id', default=None)
    loc_name = session.get('loc_name', default=None)
    wait_time_m = session.get('wait_time_m', default=0)

    if order_id is None:
        return redirect(url_for('view.order'))

    return render_template('order_complete.html', order_id=order_id, loc_name=loc_name, wait_time_m=wait_time_m)


@view.route('/order_status', methods=['GET', 'POST'])
@login_required
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
                    'is_cancelable': True if order.status.status_id == Const.WAITING else False
                }
        return jsonify(res)

    return render_template('order_status.html')


@view.route('/order_status_cancel', methods=['GET', 'POST'])
@login_required
def order_status_cancel():
    if request.method == 'POST':
        res = {
            'is_err': True
        }
        order_id = request.form['order_id']
        if order_id:
            order = db.session.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                order.status.status_id = Const.CANCELLED
                db.session.add(order)
                db.session.commit()
                res = {
                    'is_err': False,
                    'order_id': order_id,
                    'order_stats': order.status.status.name,
                    'is_cancelable': True if order.status.status_id == Const.WAITING else False,
                    'msg': '注文をキャンセルしました'
                }
        return jsonify(res)

    return render_template('order_status.html')


@view.route('/kitchen')
@login_required
def kitchen():
    tab = request.args.get('tab', default=Const.TAB_WAITING_AND_COOKING)
    items = db.session.query(Item).all()
    item_names = {}
    for i in items:
        item_names[i.id] = i.name
    master_status = db.session.query(MasterStatus).all()
    kitchen_list, total_order_count_list = get_kitchen_list(master_status)
    return render_template('kitchen.html', tab=int(tab), item_names=item_names,
                           master_status=master_status,
                           kitchen_list=kitchen_list,
                           total_order_count_list=total_order_count_list)


@view.route('/kitchen/upd', methods=['GET', 'POST'])
@login_required
def kitchen_upd():
    if request.method == 'POST':
        order_id = request.form['order_id']
        status_id = request.form['status_id']
        status_id = int(status_id)

        if status_id == Const.WAITING or status_id == Const.COOKING or status_id == Const.CARRYING:
            tab = Const.TAB_WAITING_AND_COOKING
        elif status_id == Const.COMPLETED:
            tab = Const.TAB_CARRYING_AND_COMPLETED
        else:
            tab = Const.TAB_CANCELLED

        master_status = db.session.query(MasterStatus).filter(MasterStatus.id == status_id).first()
        order_status_history = OrderStatusHistory(status=master_status)

        order = db.session.query(Order).filter(Order.id == order_id).first()

        order.status.status_id = status_id
        order.status_historys.append(order_status_history)

        db.session.add(order)
        db.session.commit()

        return jsonify({'is_err': False, 'tab': tab})

    return redirect(url_for('view.kitchen'))


@view.route('/summary', methods=['GET', 'POST'])
@login_required
def summary():
    order = db.session.query(Order).all()
    total_order_count = len(order)
    cnt_buta = 0
    cnt_modern = 0
    for o in order:
        if o.status.status_id != Const.COMPLETED:
            continue
        cnt_buta += o.count_buta
        cnt_modern += o.count_modern

    cnt_list = [cnt_buta, cnt_modern]

    items = db.session.query(Item).all()

    forms = []
    total = 0
    for idx, item in enumerate(items):
        name = item.name
        price = item.price
        odr_cnt = cnt_list[idx]
        subtotal = odr_cnt * item.price
        total += subtotal
        form = {
            'name': name,
            'price': price,
            'odr_cnt': odr_cnt,
            'subtotal': subtotal,
        }
        forms.append(form)

    return render_template('summary.html', forms=forms, total=total, total_order_count=total_order_count)


@view.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    history = db.session.query(OrderStatusHistory).order_by(OrderStatusHistory.created_at.desc()).all()
    forms = []
    for h in history:
        form = {
            'status_id': h.status_id,
            'order_id': h.order_id,
            'status_name': h.status.name,
            'created_at': h.created_at
        }
        forms.append(form)
    return render_template('history.html', forms=forms)


def get_kitchen_list(master_status):
    res = {}
    total_order_count_list = {}
    for m_s in master_status:
        order_list = []
        total_count = 0
        for o_s in m_s.order_status:
            order_id = o_s.order.id
            count_buta = o_s.order.count_buta
            count_modern = o_s.order.count_modern
            loc_id = o_s.order.loc.id
            loc_name = o_s.order.loc.name
            create_at = o_s.order.created_at
            order_info = {
                'order_id': order_id,
                'wait_time_m': 0,
                'count_buta': count_buta,
                'count_modern': count_modern,
                'loc_id': loc_id,
                'loc_name': loc_name,
                'create_at': create_at
            }
            order_list.append(order_info)
            total_count += count_buta
            total_count += count_modern
        res[m_s.id] = order_list
        total_order_count_list[m_s.id] = total_count

    # res = {
    #     {
    #         '1(status_id)': [
    #             {
    #                 'order_id': 1,
    #                 'wait_time_m': 10,
    #                 'count_buta': 1,
    #                 'count_modern': 2,
    #                 'loc_name': '7B2'
    #             },
    #         ],
    #         '2(status_id)': [
    #             {
    #                 'order_id': 1,
    #                 'wait_time_m': 10,
    #                 'count_buta': 1,
    #                 'count_modern': 2,
    #                 'loc_name': '7B2'
    #             },
    #         ],
    #     },
    # }

    return res, total_order_count_list


def get_wait_time_m(order_id):
    items = db.session.query(Item).order_by(Item.id.asc()).all()
    print(items[0])
    i_0 = items[0]
    i_1 = items[1]
    # cooking_time_buta = items[0]['cooking_time_m']
    # cooking_time_modern = items[1]['cooking_time_m']
    cooking_time_buta = i_0.cooking_time_m
    cooking_time_modern = i_1.cooking_time_m

    order, order_status = db.session.query(Order, OrderStatus).filter(Order.id == order_id).first()

    d_t = order.loc.delivery_time_m
    c_t = 0

    if order_status == Const.CARRYING:
        # d_t = order.loc.delivery_time_m
        pass
    elif order_status == Const.COOKING:
        c_t = get_cooking_wait_time_m(cooking_time_buta, order.count_buta,
                                      cooking_time_modern, order.count_modern)
    elif order_status == Const.WAITING:
        master_status = db.session.query(MasterStatus).filter(db.or_(MasterStatus.id == Const.WAITING,
                                                                     MasterStatus.id == Const.COOKING)).all()
        status = master_status.order_status
        c_b = 0
        c_m = 0
        for s in status:
            c_b += s.order.count_buta
            c_m += s.order.count_modern
        c_t = get_cooking_wait_time_m(cooking_time_buta, c_b,
                                      cooking_time_modern, c_m)

    return d_t + c_t


def get_cooking_wait_time_m(cooking_time_buta, count_buta, cooking_time_modern, count_modern):
    c_t = 0
    c_t += cooking_time_buta * math.ceil(count_buta / Const.WORK_PER_COUNT)
    c_t += cooking_time_modern * math.ceil(count_modern / Const.WORK_PER_COUNT)
    return c_t
