import os
import re
import openerp
from openerp import SUPERUSER_ID, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import image_resize_image


class res_company(osv.osv):
    _inherit = 'res.company'
    
    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        result = {}
        part_obj = self.pool.get('res.partner')
        for company in self.browse(cr, uid, ids, context=context):
            result[company.id] = {}.fromkeys(field_names, False)
            if company.partner_id:
                address_data = part_obj.address_get(cr, openerp.SUPERUSER_ID, [company.partner_id.id], adr_pref=['default'])
                if address_data['default']:
                    address = part_obj.read(cr, openerp.SUPERUSER_ID, [address_data['default']], field_names, context=context)[0]
                    for field in field_names:
                        result[company.id][field] = address[field] or False
        return result    
    
    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        """ Write the 'address' functional fields. """
        company = self.browse(cr, uid, company_id, context=context)
        if company.partner_id:
            part_obj = self.pool.get('res.partner')
            address_data = part_obj.address_get(cr, uid, [company.partner_id.id], adr_pref=['default'])
            address = address_data['default']
            if address:
                part_obj.write(cr, uid, [address], {name: value or False}, context=context)
            else:
                part_obj.create(cr, uid, {name: value or False, 'parent_id': company.partner_id.id}, context=context)
        return True    
    
    _columns = {
        'city': fields.function(_get_address_data, fnct_inv=_set_address_data, size=24, type='many2one', relation='res.city',string="City", multi='address'),
        'ck_reg_no':fields.char('KT REG NO'),
        }
