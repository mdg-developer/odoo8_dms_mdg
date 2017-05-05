from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _



class stock_landed_cost_inherit(osv.osv):
    _inherit = 'stock.landed.cost'
    _description = 'Stock Landed Cost'

    def _create_account_move_line(self, cr, uid, line, move_id, credit_account_id, debit_account_id, context=None):
        """
        Generate the account.move.line values to track the landed cost.
        """
        print 'line',line.id
        ajd_id=line.id
        cr.execute('select move_id from stock_valuation_adjustment_lines where id=%s',(ajd_id,))
        m_id=cr.fetchone()
        cr.execute('select origin from stock_move where id= %s',(m_id,))
        origin=cr.fetchone()
        cr.execute('select account_analytic_id from purchase_order where name=%s',(origin[0],))
        account_analytic_id=cr.fetchone()       
        if account_analytic_id:
            account_analytic_id=account_analytic_id[0]
        else:
            account_analytic_id=False
         
        aml_obj = self.pool.get('account.move.line')
        aml_obj.create(cr, uid, {
            'name': line.name,
            'move_id': move_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'debit': line.additional_landed_cost,
            'account_id': debit_account_id,
            'analytic_account_id': account_analytic_id or False,
            
        }, context=context)
        aml_obj.create(cr, uid, {
            'name': line.name,
            'move_id': move_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'credit': line.additional_landed_cost,
            'account_id': credit_account_id,
            'analytic_account_id': account_analytic_id or False,
            
        }, context=context)
        return True


stock_landed_cost_inherit()
    
