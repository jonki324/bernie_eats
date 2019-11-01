from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import synonym
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


class User(UserMixin, Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(20), unique=True, nullable=False)
    _password = db.Column(db.String(100), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password.strip())
    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def __init__(self, login_id, password):
        self.login_id = login_id
        self.password = password

    def __repr__(self):
        return '<User id: {}, login_id: {}>'.format(self.id, self.login_id)

    def check_password(self, password):
        return check_password_hash(self.password, password.strip())

    @classmethod
    def auth(cls, query, login_id, password):
        user = query(cls).filter(cls.login_id == login_id).first()
        return user, user and user.check_password(password)


class Item(Base):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300))
    img_file_name = db.Column(db.String(20))
    cooking_time_m = db.Column(db.Integer, default=0)

    def __init__(self, name, price, comment, img_file_name, cooking_time_m):
        self.name = name
        self.price = price
        self.comment = comment
        self.img_file_name = img_file_name
        self.cooking_time_m = cooking_time_m

    def __repr__(self):
        return '<Item id: {}, name: {}, price: {}>'.format(self.id, self.name, self.price)


class Order(Base):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    count_modern = db.Column(db.Integer, default=0)
    count_buta = db.Column(db.Integer, default=0)
    loc_id = db.Column(db.Integer, db.ForeignKey('master_loc.id'))

    loc = db.relationship('MasterLoc', back_populates='orders', uselist=False)
    status = db.relationship('OrderStatus', back_populates='order', uselist=False)
    status_historys = db.relationship('OrderStatusHistory', back_populates='order')

    def __init__(self, count_modern, count_buta, loc, status, status_history):
        self.count_modern = count_modern
        self.count_buta = count_buta
        self.loc = loc
        self.status = status
        self.status_historys.append(status_history)

    def __repr__(self):
        return '<Order id: {}, modern: {}, buta: {}>'.format(self.id, self.count_modern, self.count_buta)


class OrderStatus(Base):
    __tablename__ = 'order_status'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('master_status.id'))

    order = db.relationship('Order', back_populates='status', uselist=False)
    status = db.relationship('MasterStatus', back_populates='order_status', uselist=False)

    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return '<OrderStatus id: {}, order_id: {}, status_id: {}>'.format(self.id, self.order_id, self.status_id)


class OrderStatusHistory(Base):
    __tablename__ = 'order_status_history'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('master_status.id'))

    order = db.relationship('Order', back_populates='status_historys', uselist=False)
    status = db.relationship('MasterStatus', back_populates='order_status_history', uselist=False)

    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return '<OrderStatus id: {}, order_id: {}, status_id: {}>'.format(self.id, self.order_id, self.status_id)


class MasterStatus(Base):
    __tablename__ = 'master_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    order_status = db.relationship('OrderStatus', back_populates='status', order_by='asc(OrderStatus.order_id)')
    order_status_history = db.relationship('OrderStatusHistory', back_populates='status')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<MasterStatus id: {}, name: {}>'.format(self.id, self.name)


class MasterLoc(Base):
    __tablename__ = 'master_loc'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    delivery_time_m = db.Column(db.Integer, default=0)

    orders = db.relationship('Order', back_populates='loc')

    def __init__(self, name, delivery_time_m):
        self.name = name
        self.delivery_time_m = delivery_time_m

    def __repr__(self):
        return '<MasterLoc id: {}, name: {}, delivery_time_m: {}>'.format(self.id, self.name, self.delivery_time_m)


def init_db(app):
    db.init_app(app)


def create_master_all(user_id='user', password='a'):
    user_vals = [
        {'login_id': user_id, 'password': password}
    ]
    users = []
    for user in user_vals:
        users.append(User(login_id=user['login_id'], password=user['password']))
    db.session.add_all(users)

    # 商品
    item_vals = [
        {
            'name': '古き良き豚玉',
            'price': 300,
            'comment': 'お好み焼きの通は、「豚玉に始まって豚玉に帰る」と、言われる定番の味！どうぞお楽しみください！',
            'img_file_name': 'buta.jpg',
            'cooking_time_m': 10,
         },
        {
            'name': 'Deep_モダン',
            'price': 400,
            'comment': '豚玉では満足できないそこのあなた！ボリューム満点なこちらはいかが？',
            'img_file_name': 'modern.jpg',
            'cooking_time_m': 10,
        },
    ]
    items = []
    for item in item_vals:
        items.append(Item(name=item['name'], price=item['price'], comment=item['comment'],
                          img_file_name=item['img_file_name'], cooking_time_m=item['cooking_time_m']))
    db.session.add_all(items)

    # ステータス
    status_vals = [
        {'name': '調理待ち'},
        {'name': '調理中'},
        {'name': '配達中'},
        {'name': '注文キャンセル'},
        {'name': '完了'},
    ]
    status = []
    for sts in status_vals:
        status.append(MasterStatus(name=sts['name']))
    db.session.add_all(status)

    # 配達場所
    loc_vals = [
        {'name': '181教室', 'delivery_time_m': 0},
        {'name': '職員室(本館3階)', 'delivery_time_m': 1},
        {'name': '7B22教室', 'delivery_time_m': 5},
    ]
    locs = []
    for loc in loc_vals:
        locs.append(MasterLoc(name=loc['name'], delivery_time_m=loc['delivery_time_m']))
    db.session.add_all(locs)

    db.session.commit()
