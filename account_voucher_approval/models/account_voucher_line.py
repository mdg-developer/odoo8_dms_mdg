from openerp.osv import fields, osv

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    
    _columns = {        
        'supplier_invoice_number':fields.char('Supplier Invoice Number'),        
    }
    
    def onchange_move_line_id(self, cr, user, ids, move_line_id, context=None):
        """
        Returns a dict that contains new values and context

        @param move_line_id: latest value from user input for field move_line_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        res = {}
        move_line_pool = self.pool.get('account.move.line')
        if move_line_id:
            move_line = move_line_pool.browse(cr, user, move_line_id, context=context)
            if move_line.credit:
                ttype = 'dr'
            else:
                ttype = 'cr'
            
            if move_line.invoice:
                supplier_invoice_number = move_line.invoice.supplier_invoice_number
            else:
                supplier_invoice_number = None
                
            res.update({
                'account_id': move_line.account_id.id,
                'type': ttype,
                'supplier_invoice_number':supplier_invoice_number,
                'currency_id': move_line.currency_id and move_line.currency_id.id or move_line.company_id.currency_id.id,
            })
        return {
            'value':res,
        }
        