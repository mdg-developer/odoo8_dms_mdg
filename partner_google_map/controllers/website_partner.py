import json
import openerp
import werkzeug
from openerp import SUPERUSER_ID
from openerp.addons.web.controllers.main import WebClient
from openerp.addons.web import http
from openerp.http import request, STATIC_CACHE

from openerp.addons.website.models.website import slug, unslug

class WebsitePartner(http.Controller):#(openerp.addons.website_crm_partner_assign.controllers.main.WebsiteCrmPartnerAssign):
    
    @http.route(['/partners/<partner_id>'], type='http', auth="public", website=True)
    def partners_detail(self, partner_id, partner_name='', **post):
        print 'inherit>>>>>>>>>>',partner_id
               
        if partner_id:
            #partner = request.registry['res.partner'].browse(request.cr, SUPERUSER_ID, partner_id, context=request.context)
            #return werkzeug.utils.redirect('/web#menu_id=74&amp;action=727&amp;view_type=form&amp;model=res.partner;id=%s' % partner_id)
            return werkzeug.utils.redirect('web#id=%s&view_type=form&model=res.partner&action=727' % partner_id)
            
            
        return True    