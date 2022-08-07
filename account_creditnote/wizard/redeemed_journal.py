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
from openerp.osv import orm
from openerp.osv import fields, osv
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import datetime
import base64
import logging
from math import floor
_logger = logging.getLogger(__name__)
# header_fields = ['default_code', 'product_name', 'public_price', 'uom', 'balance_qty', 'cost_price']
header_fields = ['product', 'uom', 'real quantity', 'serial number', 'theoretical quantity', 'location', 'pack', 'serial']


class redeemed_journal(osv.osv):
    _name = 'redeemed.journal'
    _description = 'Redeemed Journal'
    
    
      
    
    _columns = {
        'state':fields.selection([
        
        ('approved','Approved'),
        ('redeemed','Redeemed'),
        ('claimed','Claimed'),
        
    ], string='Status', index=True, default='approved', copy=False),
            
        'journal_id': fields.many2one('account.journal', string='Journal'),
        

    }
    
  
    
    
    # _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
#     def default_get(self, cr, uid, fields, context=None):
#         if context is None: context = {}
#         res = super(redeemed_journal, self).default_get(cr, uid, fields, context=context)
#         partner_ids = context.get('partner_id', False)
#         if partner_ids and 'partner_id' in fields:
#             for partner_id in self.pool.get('res.partner').browse(cr, uid, partner_ids, context=context):
#                 partner = {'partner_id': partner_id.id, 'outlet_type':partner_id.outlet_type.id, 'township':partner_id.township.id, 'address':partner_id.street, 'delivery_team_id':partner_id.delivery_team_id.id, 'branch_id':partner_id.branch_id.id}
#                 res.update(partner)
#         return res
    
                              
    def close(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
    
    def create_journal(self,cr,uid,ids,journal_id,credit,context=None):
        move_Obj = self.pool.get('account.move')
        journal = self.pool.get('account.journal').browse(cr,uid,journal_id[0],context=context)
        account_move = {
                                        'journal_id': journal.id,
                                        'state': 'draft',
                                        'date': credit.approved_date,
                                        'amount': credit.amount,
                                        'ref': credit.name,
                                        'partner_id': credit.customer_id.id,
                                        'branch_id': credit.branch_id.id,
                                        
                                        }
        company_id = credit.create_uid.company_id.id
        cr.execute("select * from account_period where %s >=date_start and %s <=date_stop", (credit.approved_date, credit.approved_date,))         
        period_id = cr.fetchone()[0]
        
        move_id = move_Obj.create(cr, uid, account_move, context=context)
        cr.execute("""insert into account_move_line (partner_id,name,account_id,date_maturity,move_id,credit,debit,journal_id,date,company_id,period_id) 
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),
                  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                  ( credit.customer_id.id,credit.name , journal.default_debit_account_id.id,  credit.used_date, move_id, 0.0, credit.amount, journal.id, credit.used_date,company_id, period_id, 
                   credit.customer_id.id,credit.name,credit.principle_id.property_difference_receivable_account.id,credit.used_date, move_id, credit.amount, 0.0, journal.id, credit.used_date,company_id, period_id, ))
        
    def confirm(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        state=data['state']
        journal_id = data['journal_id']
        active_ids = context.get('active_ids', []) or []
        creditnote_obj = self.pool['account.creditnote']
        for credit in creditnote_obj.browse(cr, uid, active_ids, context=context):
            if state == 'approved':
                creditnote_obj.set_to_approved(cr, uid, credit.id, context=context)
            elif state == 'claimed':
                if not credit.principle_id:
                        raise osv.except_osv(_('Configuration Error!'), _('Please select the principle.'))
                    
                creditnote_obj.write(cr, uid, credit.id, {'state':'claimed','used_date':fields.date.context_today(self,cr,uid,context=context)}, context=context)
                self.create_journal(cr, uid, ids, journal_id, credit, context=context)
            
        # import_file = data.sl_data
        # print 'file',data.sl_data

                   
redeemed_journal()

  

