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
    
    def get_foc_cashorcredit(self,cr,uid,move,context=None):
        type = None
        if move.picking_id.origin:
            if len(move.picking_id.origin)>0:
                cr.execute("""select payment_type from sale_order where name=%s""",(move.picking_id.origin,))
                type_data = cr.fetchall()
                if type_data:
                    type = type_data[0][0]
        return type
    
    def _account_entry_move_foc_clearance(self, cr, uid, quants, move, context=None):
        """
        Accounting Valuation Entries

        quants: browse record list of Quants to create accounting valuation entries for. Unempty and all quants are supposed to have the same location id (thay already moved in)
        move: Move to use. browse record
        """
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(cr, uid, location_from, context=context)
        company_to = location_obj._location_owner(cr, uid, location_to, context=context)

        if move.product_id.valuation != 'real_time':
            return False
        for q in quants:
            if q.owner_id:
                #if the quant isn't owned by the company, we don't make any valuation entry
                return False
            if q.qty <= 0:
                #we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
                #At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
                #to make the adjustments when we know the real cost price.
                return False

        #in case of routes making the link between several warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        # Create Journal Entry for products arriving in the company
        if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_to.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
            if location_from and location_from.usage == 'customer':
                #goods returned from customer
                self._create_account_move_line(cr, uid, quants, move, acc_dest, acc_valuation, journal_id, context=ctx)
            else:
                self._create_account_move_line(cr, uid, quants, move, acc_src, acc_valuation, journal_id, context=ctx)

        # Create Journal Entry for products leaving the company
        if company_from and (move.location_id.usage == 'internal' and move.location_dest_id.usage not in ('internal', 'transit') or company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_from.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
            if location_to and location_to.usage == 'supplier':
                #goods returned to supplier
                self._create_account_move_line(cr, uid, quants, move, acc_valuation, acc_src, journal_id, context=ctx)
            else:
                self._create_account_move_line(cr, uid, quants, move, acc_valuation, acc_dest, journal_id, context=ctx)
    
    def _get_accounting_data_for_valuation_foc_ar(self, cr, uid, move, context=None):
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
                type = self.get_foc_cashorcredit(cr, uid, move, context)
                if type == 'cash':
                    acc_dest = move.product_id.categ_id.property_account_foc_cash.id
                elif type == 'credit':
                    acc_dest = move.product_id.categ_id.property_account_foc_credit.id    
            else:
                acc_dest = accounts['stock_account_output']
        acc_valuation = accounts.get('property_stock_valuation_account_id', False)
        journal_id = accounts['stock_journal']

        return journal_id, acc_src, acc_dest, acc_valuation 
         
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
                print 'quant>>>',move.quant_ids
                type = self.get_foc_cashorcredit(cr, uid, move, context)
                if type == 'cash':
                    acc_dest = move.product_id.categ_id.property_account_foc_cash.id
                    #self._create_account_move_line(cr, uid, move.quant_ids, move, move.product_id.categ_id.property_account_foc_cash.id, move.product_id.categ_id.property_account_foc_principle_receivable.id, accounts['stock_journal'], context)
                elif type == 'credit':
                    acc_dest = move.product_id.categ_id.property_account_foc_credit.id    
                    #self._create_account_move_line(cr, uid, move.quant_ids, move, move.product_id.categ_id.property_account_foc_credit.id, move.product_id.categ_id.property_account_foc_principle_receivable.id, accounts['stock_journal'], context)
            else:
                acc_dest = accounts['stock_account_output']
        acc_valuation = accounts.get('property_stock_valuation_account_id', False)
        journal_id = accounts['stock_journal']

        return journal_id, acc_src, acc_dest, acc_valuation    