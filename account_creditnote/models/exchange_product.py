from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class exchange_product(osv.osv):
    _inherit = "product.transactions"
    
    _columns = {
                'exchange_type':fields.selection([('Exchange', 'Exchange'), ('Sale Return', 'Sale Return'),('Sale Return with Credit Note', 'Sale Return with Credit Note') ], 'Type',required=True),
                'credit_note_id': fields.many2one('account.creditnote', 'Credit Note', readonly=True),
              }

    def create_credit_note(self, cr, uid, ids, context=None):

        product_obj = self.pool.get('product.transactions')
        credit_note_obj = self.pool.get('account.creditnote')
        program_obj = self.pool.get('program.form.design')
        if ids:
            product_value = product_obj.browse(cr, uid, ids[0], context=context)
            if product_value.exchange_type == 'Sale Return with Credit Note':
                program = program_obj.search(cr, uid, [('return_claim', '=', True)], context=context)
                if program:
                    program_value = program_obj.browse(cr, uid, program, context=context)
                    cn_data = {
                        'customer_id': product_value.customer_id.id,
                        'program_id': program_value.id,
                        'amount': product_value.total_value,
                        'sales_return_id': product_value.id,
                    }
                    credit_note_id = credit_note_obj.create(cr, uid, cn_data, context=context)
                    product_value.write({'credit_note_id': credit_note_id})
                    credit_note_obj.set_to_approved(cr, uid, [credit_note_id], context=context)