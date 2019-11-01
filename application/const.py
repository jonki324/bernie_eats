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
        CANCELLED: 'secondary'
    }

    TAB_WAITING_AND_COOKING = 1
    TAB_CARRYING_AND_COMPLETED = 2
    TAB_CANCELLED = 3

    DISPLAY_COUNT = 20

    WORK_PER_COUNT = 4
