from .common import register_handlers_common
from .photo import register_photo_handlers
from .user import register_user_handlers
from .congratulation import register_congratulation_handlers
from .help import helper_inline_button

def register_handlers(dp):
    register_handlers_common(dp)
    register_photo_handlers(dp)
    register_user_handlers(dp)
    register_congratulation_handlers(dp)
    helper_inline_button(dp)
