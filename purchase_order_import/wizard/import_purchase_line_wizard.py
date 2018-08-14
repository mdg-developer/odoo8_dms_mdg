# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# import time
import base64, StringIO, csv
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
import xlrd
from xlrd import open_workbook
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

header_fields = ['suppliercode', 'qty', 'uom', 'price']


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
purchase_order()

# class journal_entries_line_customize(osv.osv):
class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'  
    _order = "id asc"
   
    def _default_get(self, cr, uid, fields, context=None):
        # default_get should only do the following:
        #   -propose the next amount in debit/credit in order to balance the move
        #   -propose the next account from the journal (default debit/credit account) accordingly
        context = dict(context or {})
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        tax_obj = self.pool.get('account.tax')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        partner_obj = self.pool.get('res.partner')
        currency_obj = self.pool.get('res.currency')
        account_move_line_obj = self.pool.get('account.move.line')
        debitTotal = 0.0
        creditTotal = 0.0
#         count = 0
        if not context.get('journal_id', False):
            context['journal_id'] = context.get('search_default_journal_id', False)
        if not context.get('period_id', False):
            context['period_id'] = context.get('search_default_period_id', False)
        context = self.convert_to_period(cr, uid, context)
        print 'default_get'
        # Compute simple values
        data = super(purchase_order_line, self)._default_get(cr, uid, fields, context=context)
  
        if context.get('journal_id'):
            total = 0.0
            
            # in account.move form view, it is not possible to compute total debit and credit using
            # a browse record. So we must use the context to pass the whole one2many field and compute the total
            if context.get('line_id'):
                for l in context.get('line_id'):
                    print 'Line ', l
                    if 'debit' in str(l):
                        debitTotal += l[2]['debit']
                    if 'credit' in str(l):
                        creditTotal += l[2]['credit']
                    if l[0] == 4:
                        move_lines = self.pool.get('account.move.line').browse(cr, uid, l[1], context=context)
                        debitTotal += move_lines.debit
                        creditTotal += move_lines.credit
                        
                if debitTotal != creditTotal:
                
                    for move_line_dict in move_obj.resolve_2many_commands(cr, uid, 'line_id', context.get('line_id'), context=context):
#                        if count == 0:
                        if move_line_dict.get('id'):
                            print 'Update the deleted lines with latest lines', move_line_dict
                            total += move_line_dict.get('debit', 0.0) - move_line_dict.get('credit', 0.0)
                        else:
                            print 'Move line without id'
                            data['name'] = move_line_dict.get('name')
                            data['ref'] = move_line_dict.get('ref')
                            # data['account_id'] = move_line_dict.get('account_id')
                            data['partner_id'] = move_line_dict.get('partner_id')
                            data['currency_rate'] = move_line_dict.get('currency_rate')
                            data['amount_currency'] = move_line_dict.get('amount_currency') * -1
                            data['analytic_account_id'] = move_line_dict.get('analytic_account_id')
                            data['account_tax_id'] = move_line_dict.get('account_tax_id')
                            data['date'] = move_line_dict.get('date')
                            data['tax_amount'] = move_line_dict.get('tax_amount')
                            data['account_id'] = move_line_dict.get('account_id')
                            data['location_id'] = move_line_dict.get('location_id')
                            total += move_line_dict.get('debit', 0.0) - move_line_dict.get('credit', 0.0)
#                                 count += 1
                else:
                    for move_line_dict in move_obj.resolve_2many_commands(cr, uid, 'line_id', context.get('line_id'), context=context):
                        print 'Now Updating.....'
                        data['name'] = None
                        data['ref'] = None
                        data['partner_id'] = None
                        data['currency_rate'] = None
                        data['amount_currency'] = None
                        data['analytic_account_id'] = None
                        data['account_tax_id'] = None
                        data['date'] = None
                        data['tax_amount'] = None
                        data['account_id'] = None
                        data['location_id'] = None
                            
               
            elif context.get('period_id'):
                # find the date and the ID of the last unbalanced account.move encoded by the current user in that journal and period
                move_id = False
                cr.execute('''SELECT move_id, date FROM account_move_line
                    WHERE journal_id = %s AND period_id = %s AND create_uid = %s AND state = %s
                    ORDER BY id DESC limit 1''', (context['journal_id'], context['period_id'], uid, 'draft'))
                res = cr.fetchone()
                move_id = res and res[0] or False
                data['date'] = res and res[1] or period_obj.browse(cr, uid, context['period_id'], context=context).date_start
                data['move_id'] = move_id
                if move_id:
                    # if there exist some unbalanced accounting entries that match the journal and the period,
                    # we propose to continue the same move by copying the ref, the name, the partner...
                    move = move_obj.browse(cr, uid, move_id, context=context)
                    data.setdefault('name', move.line_id[-1].name)
                    for l in move.line_id:
                        data['partner_id'] = data.get('partner_id') or l.partner_id.id
                        # data['partner_id'] =  l.partner_id.id
                        data['ref'] = data.get('ref') or l.ref
                       
                        total += (l.debit or 0.0) - (l.credit or 0.0)

            # compute the total of current move
            data['debit'] = total < 0 and -total or 0.0
            data['credit'] = total > 0 and total or 0.0
            
            print 'Debit Total => ', debitTotal
            print 'Credit Total => ', creditTotal
            # pick the good account on the journal accordingly if the next proposed line will be a debit or a credit
            journal_data = journal_obj.browse(cr, uid, context['journal_id'], context=context)
            account = total > 0 and journal_data.default_credit_account_id or journal_data.default_debit_account_id
            # map the account using the fiscal position of the partner, if needed
            if isinstance(data.get('partner_id'), (int, long)):
                part = partner_obj.browse(cr, uid, data['partner_id'], context=context)
            elif isinstance(data.get('partner_id'), (tuple, list)):
                part = partner_obj.browse(cr, uid, data['partner_id'][0], context=context)
            else:
                part = False
            if account and part:
                account = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, account.id)
                account = account_obj.browse(cr, uid, account, context=context)
                
        data = self._default_get_move_form_hook(cr, uid, data)
        print 'data=>', data
        return data
purchase_order_line()


class pol_import(orm.TransientModel):
    _name = 'pol.import'
    _description = 'Import purchase order lines'
    _columns = {
        'pol_data': fields.binary('File', required=True),
        'pol_fname': fields.char('Filename', size=128),
        'note':fields.text('Log'),
    }
    _defaults = {
        'pol_fname': '',
    }

    def pol_import(self, cr, uid, ids, context=None):
        po_obj = self.pool.get('purchase.order')
        pol_obj = self.pool.get('purchase.order.line')
        mod_obj = self.pool.get('ir.model.data')
        company_id = context['company_id']
        order_id = context['order_id']
        product_obj = self.pool.get('product.product')


        result_view = mod_obj.get_object_reference(cr, uid, 'purchase_order_import', 'pol_import_result_view')
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        data = self.browse(cr, uid, ids)[0]
        aml_file = data.pol_data


        err_log = ''
        header_line = False

        lines = base64.decodestring(aml_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = []
        for s in wb.sheets():
            # header
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
            # add header
            excel_rows.append(headers)
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                excel_rows.append(values)
        amls = []

        for ln in excel_rows:

            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue

            # process header line
            if not header_line:
                if ln[0].strip().lower() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your CSV separator as well as the column header fields") % ln)
                else:
                    header_line = True
                    # locate first column with empty header
                    column_cnt = 0
                    supplier_code_i = qty_i = uom_i = credit_i = price_i  = None
                    for cnt in range(len(ln)):
                        if ln[cnt] == '':
                            column_cnt = cnt
                            break
                        elif cnt == len(ln) - 1:
                            column_cnt = cnt + 1
                            break
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid CSV File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'suppliercode':
                            supplier_code_i = i
                        elif header_field == 'qty':
                            qty_i = i
                        elif header_field == 'uom':
                            uom_i = i
                        elif header_field == 'price':
                            price_i = i
                    for f in [(supplier_code_i, 'suppliercode'), (qty_i, 'qty'), (uom_i, 'uom'), (price_i, 'price')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is missing !") % f[1]

            # process data lines
            else:
                if ln and ln[0] and ln[0][0] not in ['#', '']:

                    aml_vals = {}
                    product_ids=None
                    product_name=None
                    
                    result = {}
                    if ln[supplier_code_i]: 
                        products = str(ln[supplier_code_i]).strip()
                    if products:
                        suppliercode_name = products  # '['+product_code+'] '+      
    
                    if suppliercode_name:
                        cr.execute(""" select id,name_template from product_product where lower(supplier_code) = %s """, (suppliercode_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            product_ids = data[0][0]
                            product_name = data[0][1]
#                         if supplier_code_ids:
#                             supplier_code_id = supplier_code_ids[0]
#                             productObj = product_obj.browse(cr, uid, supplier_code_id, context=None)
#                             uom_ids = productObj.uom_id.id
                        else:
                            raise osv.except_osv(_('User Error!'),
                                         _("This Supplier Code doesn't exist in ther System.\n Suppler Code: %s")% suppliercode_name)
                    if ln[uom_i]: 
                        uoms = str(ln[uom_i]).strip()
                    if uoms:
                        uom_name = uoms  
    
                    if uom_name:
                        cr.execute(""" select id from product_uom where lower(name) = %s """, (uom_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            uom_ids = data[0]
                    if order_id:
                        cr.execute(""" select date_order from purchase_order where id= %s """, ([order_id]))
                        data = cr.fetchall()
                        if data:
                            date_planned = data[0]
                        
                    aml_vals['order_id'] = order_id
                    aml_vals['product_id'] = product_ids
                    aml_vals['name'] = product_name
                    aml_vals['supplier_code'] = suppliercode_name
                    aml_vals['state'] = 'draft'
                    aml_vals['date_planned'] = date_planned                    
                    aml_vals['product_qty'] = ln[qty_i]                   
                    aml_vals['product_uom'] = uom_ids
                    aml_vals['price_unit'] = ln[price_i]
                    
                    pol_obj.create(cr, uid, aml_vals,context=context)
                    amls.append((0, 0, aml_vals)) 
 
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            return {
                'name': _('Import File result'),
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pol.import',
                'view_id': [result_view[1]],
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        else:
            amls = sorted(amls)
            print amls            

            #po_obj.write(cr, uid, [order_id], {'order_id': amls})
            return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
