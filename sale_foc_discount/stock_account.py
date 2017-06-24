from openerp.osv import fields, osv
from openerp.osv import orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
import logging
_logger = logging.getLogger(__name__)

class stock_quant(osv.osv):
    _inherit = "stock.quant"


#     def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
#         """
#         Return the accounts and journal to use to post Journal Entries for the real-time
#         valuation of the quant.
# 
#         :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
#         :returns: journal_id, source account, destination account, valuation account
#         :raise: osv.except_osv() is any mandatory account or journal is not defined.
#         """
#         product_obj = self.pool.get('product.template')
#         accounts = product_obj.get_product_accounts(cr, uid, move.product_id.product_tmpl_id.id, context)
#         foc_account_id=move.company_id.foc_account_id.id
#         if foc_account_id is False:
#             raise orm.except_orm(_('Error :'), _("Please select Sale FOC Account in Account setting!"))
#         if move.location_id.valuation_out_account_id:
#             acc_src = move.location_id.valuation_out_account_id.id
#         else:
#             acc_src = accounts['stock_account_input']
#         print 'foc_account_id',move.foc,foc_account_id
#        
#         if move.location_dest_id.valuation_in_account_id:
#             acc_dest = move.location_dest_id.valuation_in_account_id.id
#         else:
#             
#             if move.foc:
#                 acc_dest = foc_account_id
#             
#             else:
#                 acc_dest = accounts['stock_account_output']
# 
#         acc_valuation = accounts.get('property_stock_valuation_account_id', False)
#         journal_id = accounts['stock_journal']
#         return journal_id, acc_src, acc_dest, acc_valuation
    
    
    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the quant.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :returns: journal_id, source account, destination account, valuation account
        :raise: osv.except_osv() is any mandatory account or journal is not defined.
        """
        product_obj = self.pool.get('product.template')
        accounts = product_obj.get_product_accounts(cr, uid, move.product_id.product_tmpl_id.id, context)
        foc_account_id=move.company_id.foc_account_id.id
        if foc_account_id is False:
            raise orm.except_orm(_('Error :'), _("Please select Sale FOC Account in Account setting!"))            
        if move.location_id.valuation_out_account_id:
            acc_src = move.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts['stock_account_input']

        if move.location_dest_id.valuation_in_account_id:
            acc_dest = move.location_dest_id.valuation_in_account_id.id
        else:
            if move.foc:
                acc_dest = foc_account_id
            
            else:
                acc_dest = accounts['stock_account_output']
        acc_valuation = accounts.get('property_stock_valuation_account_id', False)
        journal_id = accounts['stock_journal']

        return journal_id, acc_src, acc_dest, acc_valuation    