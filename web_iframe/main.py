from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
import datetime
import time

from openerp.tools.translate import _

class web_iframe(http.Controller):

    @http.route(['/user_sales_team'], type='json', auth="public", website=True)
    def get_user_sales_team(self, user_id, remove=False, unlink=False, order_id=None, token=None, **post):
        user = request.registry.get('res.users').browse(request.cr, SUPERUSER_ID, int(user_id))
        return user.section_ids.ids