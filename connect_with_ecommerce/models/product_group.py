from openerp import api,fields, models, _
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
import logging

_logger = logging.getLogger(__name__)

# shl
class product_group(osv.osv):
    _inherit = 'product.group'

    _columns={
        'code':fields.integer('Code',copy=False),
    }

    _sql_constraints = [('code_uniq', 'unique(code)',
                                'Code should not be same to others!')
                ]

class product_principal(osv.osv):
    _inherit = 'product.maingroup'

    _columns = {
        'code': fields.char('Code',copy=False)
    }
    _sql_constraints = [('code_uniq', 'unique(code)',
                            'Code should not be same to others!')
            ]

    def create(self, cursor, user, vals, context=None):

        principal_code = vals.get('code') or False
        if principal_code:
            cursor.execute(""" insert into principal_category_code (principal_code) VALUES (%s) """,(principal_code,))

        code = vals.get('code')
        max_size = 3
        if code:
            if len(code) > max_size:
                raise osv.except_osv(_('Warning!'),_('Code should be 3 digits!'))
        return super(product_principal, self).create(cursor, user, vals, context=context)

    def write(self, cursor, user, ids, vals, context=None):

        principal_code = vals.get('code') or False
        if principal_code:
            cursor.execute(""" insert into principal_category_code (principal_code) VALUES (%s) """,(principal_code,))

        code = vals.get('code')
        max_size = 3
        if code:
            if len(code) > max_size:
                raise osv.except_osv(_('Warning!'),_('Code should be 3 digits!'))

        return super(product_principal, self).write(cursor, user, ids, vals, context=context)
    
class product_category(osv.osv):
    _inherit = 'product.category'

    _columns = {
        'principal_id': fields.many2one('product.maingroup','Product Principal'),
        'code': fields.char('Code',copy=False),
        'is_code_generated': fields.boolean('Is Code Generated')
    }
    _sql_constraints = [('code_uniq', 'unique(code)',
                            'Code should not be same to others!')
            ]

    _defaults = {
        'code':False
    }

    def action_generate_category_code(self, cr, uid, ids, context=None):
        vals = {}
        code = False
        for category in self.browse(cr, uid, ids):
            principal_data = category.principal_id
            if principal_data:
                principal_code = principal_data.code
                if principal_code:
                    cr.execute("""select id,principal_code, category_code from principal_category_code where principal_code = %s order by category_code desc limit 1""", (principal_code,))
                    records = cr.dictfetchall()
                    for rec in records:
                        if rec['principal_code'] != None:
                            category_code = rec['category_code']
                            if category_code:
                                category_code = int(category_code)+1
                                category_code = "%03d" % category_code
                                cr.execute("""insert into principal_category_code (principal_code,category_code,category_id) values (%s,%s,%s)""",(rec['principal_code'],category_code,category.id,))
                            else:
                                category_code = '001'
                                cr.execute("""update principal_category_code set category_code = %s where id = %s""",(category_code,rec['id'],))
                            code = rec['principal_code'] + str(category_code)
                            if code:
                                vals.update({
                                    'code':code,
                                    'is_code_generated':True
                                })
        return self.write(cr, uid, ids, vals, context=context)

class principal_category_code(osv.osv):
    _name = 'principal.category.code'
    _columns = {
        'principal_code': fields.char('Principal Code'),
        'category_code': fields.char('Category Code', size=3),
        'sku_code': fields.char('SKU Code', size=3),
        'category_id': fields.many2one('product.category',"Product Category"),
    }