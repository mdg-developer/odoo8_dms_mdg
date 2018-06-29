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
    
    def get_foc_cashorcredit(self, cr, uid, move, context=None):
        type = None
        if move.picking_id.origin:
            if len(move.picking_id.origin) > 0:
                cr.execute("""select payment_type from sale_order where name=%s""", (move.picking_id.origin,))
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
                # if the quant isn't owned by the company, we don't make any valuation entry
                return False
            if q.qty <= 0:
                # we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
                # At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
                # to make the adjustments when we know the real cost price.
                return False

        # in case of routes making the link between several warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        # Create Journal Entry for products arriving in the company
        if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_to.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
            if location_from and location_from.usage == 'customer':
                # goods returned from customer
                self._create_account_move_line(cr, uid, quants, move, acc_dest, acc_valuation, journal_id, context=ctx)
            else:
                self._create_account_move_line(cr, uid, quants, move, acc_src, acc_valuation, journal_id, context=ctx)

        # Create Journal Entry for products leaving the company
        if company_from and (move.location_id.usage == 'internal' and move.location_dest_id.usage not in ('internal', 'transit') or company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_from.id
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, context=ctx)
            if location_to and location_to.usage == 'supplier':
                # goods returned to supplier
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
        foc_account_id = move.company_id.foc_account_id.id
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

    # cutomize stock journal clearance
    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        if context.get('force_valuation_amount'):
            valuation_amount = context.get('force_valuation_amount')
        else:
            if move.product_id.cost_method == 'average':
                valuation_amount = cost if move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal' else move.product_id.standard_price
            else:
                valuation_amount = cost if move.product_id.cost_method == 'real' else move.product_id.standard_price
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        valuation_amount = currency_obj.round(cr, uid, move.company_id.currency_id, valuation_amount * qty)
        partner_id = (move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(move.picking_id.partner_id).id) or False
        if move.foc:
            # type = self.get_foc_cashorcredit(cr, uid, move, context)
            type = 'cash'
            if type == 'cash':
                credit_account_id_1 = move.product_id.categ_id.property_account_foc_cash.id 
                debit_account_id_1 = move.product_id.categ_id.property_account_foc_principle_receivable.id
                if credit_account_id_1 is False:
                    raise orm.except_orm(_('Error :'), _("Please select FOC Cash Account in Product Category %s!")) % move.product_id.categ_id.name 
                
                if debit_account_id_1 is False:
                    raise orm.except_orm(_('Error :'), _("Please select FOC Principle Account Receivable in Product Category %s!")) % move.product_id.categ_id.name          
#                 debit_account_id_1 = move.product_id.categ_id.property_account_foc_cash.id 
#                 credit_account_id_1 =move.product_id.categ_id.property_account_foc_principle_receivable.id                
            elif type == 'credit':
                credit_account_id_1 = move.product_id.categ_id.property_account_foc_credit.id 
                debit_account_id_1 = move.product_id.categ_id.property_account_foc_principle_receivable.id  
                if credit_account_id_1 is False:
                    raise orm.except_orm(_('Error :'), _("Please select FOC Credit Account in Product Category %s!")) % move.product_id.categ_id.name 
                
                if debit_account_id_1 is False:
                    raise orm.except_orm(_('Error :'), _("Please select FOC Principle Account Receivable in Product Category %s!")) % move.product_id.categ_id.name                  
#                 debit_account_id_1 = move.product_id.categ_id.property_account_foc_credit.id 
#                 credit_account_id_1 = move.product_id.categ_id.property_account_foc_principle_receivable.id
            income_account_id_1 = move.product_id.categ_id.property_account_foc_income.id 
            if income_account_id_1 is False:
                raise orm.except_orm(_('Error :'), _("Please select FOC Income Account  in Product Category %s!")) % move.product_id.categ_id.name                  
            pricelist_id = move.product_id.product_tmpl_id.main_group.pricelist_id.id  
            principle_partner_id = move.product_id.product_tmpl_id.main_group.partner_id.id  
            if principle_partner_id is False:
                raise orm.except_orm(_('Error :'), _("Please select Partner in Product Principle %s!")) % move.product_id.product_tmpl_id.main_group.name                  
            
            
            product_price = 0
            income_price=0
            if pricelist_id:
                product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context=context)
                cr.execute("select new_price from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s) and product_id=%s and product_uom_id=%s", (pricelist_id, product.id, product.product_tmpl_id.uom_id.id,))
                product_price_data = cr.fetchone()[0]     
                product_price =qty * product_price_data
                if valuation_amount >=0:
                    income_price = product_price - valuation_amount
                if valuation_amount < 0:
                    income_price =  - product_price + (-1*valuation_amount)
                    

               
                
            debit_line_vals = {
                        'name': move.name,
                        'product_id': move.product_id.id,
                        'quantity': qty,
                        'product_uom_id': move.product_id.uom_id.id,
                        'ref': move.picking_id and move.picking_id.name or False,
                        'date': move.date,
                        'partner_id': partner_id,
                        'debit': valuation_amount > 0 and valuation_amount or 0,
                        'credit': valuation_amount < 0 and -valuation_amount or 0,
                        'account_id': debit_account_id,
            }
            credit_line_vals = {
                        'name': move.name,
                        'product_id': move.product_id.id,
                        'quantity': qty,
                        'product_uom_id': move.product_id.uom_id.id,
                        'ref': move.picking_id and move.picking_id.name or False,
                        'date': move.date,
                        'partner_id': partner_id,
                        'credit': valuation_amount > 0 and valuation_amount or 0,
                        'debit': valuation_amount < 0 and -valuation_amount or 0,
                        'account_id': credit_account_id,
            }    
            debit_line_vals1 = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': principle_partner_id,
                    'debit': product_price > 0 and product_price or 0,
                    'credit': product_price < 0 and -product_price or 0,
                    'account_id': debit_account_id_1,
                }
          
            credit_line_vals1 = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'credit': valuation_amount > 0 and valuation_amount or 0,
                    'debit': valuation_amount < 0 and -valuation_amount or 0,
                    'account_id': credit_account_id_1,
            }
            credit_line_vals2 = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'quantity': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': principle_partner_id,
                    'credit': income_price > 0 and income_price or 0,
                    'debit': income_price < 0 and -income_price or 0,
                    'account_id': income_account_id_1,
            }            
            return [(0, 0, debit_line_vals), (0, 0, credit_line_vals), (0, 0, debit_line_vals1), (0, 0, credit_line_vals1), (0, 0, credit_line_vals2)]    
        else:
            debit_line_vals = {
                        'name': move.name,
                        'product_id': move.product_id.id,
                        'quantity': qty,
                        'product_uom_id': move.product_id.uom_id.id,
                        'ref': move.picking_id and move.picking_id.name or False,
                        'date': move.date,
                        'partner_id': partner_id,
                        'debit': valuation_amount > 0 and valuation_amount or 0,
                        'credit': valuation_amount < 0 and -valuation_amount or 0,
                        'account_id': debit_account_id,
            }
            credit_line_vals = {
                        'name': move.name,
                        'product_id': move.product_id.id,
                        'quantity': qty,
                        'product_uom_id': move.product_id.uom_id.id,
                        'ref': move.picking_id and move.picking_id.name or False,
                        'date': move.date,
                        'partner_id': partner_id,
                        'credit': valuation_amount > 0 and valuation_amount or 0,
                        'debit': valuation_amount < 0 and -valuation_amount or 0,
                        'account_id': credit_account_id,
            }
            return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        
            
    
                 
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
        foc_account_id = move.company_id.foc_account_id.id
            
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
                journal_id = None
                cr.execute("""select id from account_journal where lower(name) like '%miscellaneous%'""")
                journal_data = cr.fetchall()
                if journal_data:
                    journal_id = journal_data[0][0]
                    
                acc_dest = foc_account_id
                print 'quant>>>', move.quant_ids
                type = self.get_foc_cashorcredit(cr, uid, move, context)
                if type == 'cash':
                    acc_dest = move.product_id.categ_id.property_account_foc_cash.id
                    # self._create_account_move_line(cr, uid, move.quant_ids, move, move.product_id.categ_id.property_account_foc_cash.id, move.product_id.categ_id.property_account_foc_principle_receivable.id, journal_id, context)
                elif type == 'credit':
                    acc_dest = move.product_id.categ_id.property_account_foc_credit.id    
                    # self._create_account_move_line(cr, uid, move.quant_ids, move, move.product_id.categ_id.property_account_foc_credit.id, move.product_id.categ_id.property_account_foc_principle_receivable.id, journal_id, context)
            else:
                if  move.issue_type == 'donation':
                    acc_dest = move.product_id.product_tmpl_id.main_group.property_donation_account.id
                elif  move.issue_type == 'sampling':
                    acc_dest = move.product_id.product_tmpl_id.main_group.property_sampling_account.id           
                elif  move.issue_type == 'other':
                    acc_dest = move.product_id.product_tmpl_id.main_group.property_uses_account.id
                else:                      
                    acc_dest = accounts['stock_account_output']
                
        acc_valuation = accounts.get('property_stock_valuation_account_id', False)
        journal_id = accounts['stock_journal']

        return journal_id, acc_src, acc_dest, acc_valuation    
