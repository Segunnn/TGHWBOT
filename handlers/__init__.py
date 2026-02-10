from .common import router as common_router
from .add_hw import router as add_hw_router
from .start import router as start_router
from .list_hw import router as list_hw_router
#from .get_sticker_id import router as sticker_router

routers = [list_hw_router, common_router, add_hw_router, start_router]

from .somecoolshit import days_until_deadline