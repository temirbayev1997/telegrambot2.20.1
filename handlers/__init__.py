from .common import register_common_handlers
from .photo import register_photo_handlers
from .user import register_user_creation_handlers
from .congratulation import register_congratulation_handlers

def register_handlers(dp):
    register_common_handlers(dp)
    register_photo_handlers(dp)
    register_user_creation_handlers(dp)
    register_congratulation_handlers(dp)
