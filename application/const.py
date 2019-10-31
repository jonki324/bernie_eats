class Const(object):
    ITEM_ID_BUTA = 1
    ITEM_ID_MODERN = 2

    WAITING = 1
    COOKING = 2
    CARRYING = 3
    CANCELLED = 4
    COMPLETED = 5

    COLORS = {
        WAITING: 'danger',
        COOKING: 'warning',
        CARRYING: 'info',
        COMPLETED: 'success',
    }
