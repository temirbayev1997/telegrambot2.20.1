from .common import register_handlers_common
from .photo import register_photo_handlers
from .user import register_user_handlers
from .congratulation import register_congratulation_handlers
from .booking import booking_user_handlers


def register_handlers(dp):
    register_handlers_common(dp)
    register_photo_handlers(dp)
    register_user_handlers(dp)
    register_congratulation_handlers(dp)
    booking_user_handlers(dp)