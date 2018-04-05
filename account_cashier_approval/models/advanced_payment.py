from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
import locale

class crm_case_section(osv.osv):
    _inherit = "crm.case.section"
    _description = "Sales Denomination"         
    _columns = {
        'team_partner_id':fields.many2one('res.partner', 'Partner ID' , required=False),
        }
    
class manual_sale_denomination(osv.osv):
    
    _name = "manual.sales.denomination"
    _description = "Sales Denomination"         
    
    def _deno_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}        
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0            
            for line in order.denomination_note_line:
                note_data=self.pool.get('manual.sales.denomination.note.line').browse(cr, uid, line.id, context=context)
                note = note_data.notes
                note=note.replace(',','')
                qty = note_data.note_qty
                val1 += (float(note) * float(qty))                           
            res[order.id]= val1
        return res  
    

    
    def _get_plusorminus_diff_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}                
        dssr_deno_amount=self._deno_amount(cr, uid, ids, field_name, arg, context=context)
        for k, dssr_deno_amount in dssr_deno_amount.iteritems():
            dssr_deno_amount=dssr_deno_amount 
             
        val1=0.0
        sign = ""
        for order in self.browse(cr, uid, ids, context=context):

            val1=order.invoice_total - dssr_deno_amount
            sign = str(val1)
            if val1 > 0:

                sign = "(Deficit) " + str(val1)
            elif val1 < 0:
                val1 = val1 * -1
           
                sign = "(Surplus) " + str(val1)
                                      
            res[order.id]= sign 
        return res  
    
    
    _columns = {
        'date':fields.datetime('Date'),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'user_id':fields.many2one('res.users', 'Salesman Name'  , required=True, select=True, track_visibility='onchange'),
        'name':fields.char('Txn' , readonly=True),
        'invoice_count':fields.integer('Invoiced' , readonly=False),
       'denomination_note_line':fields.one2many('manual.sales.denomination.note.line', 'denomination_note_ids', string='Sale denomination Product Line', copy=True),
        'note':fields.text('Note'),    
      'partner_id':fields.many2one('res.partner', string='Partner'),
    'total_amount':fields.function(_deno_amount, string='Denomination Total', digits_compute=dp.get_precision('Product Price'),type='float'),
    'sign_diff_amount': fields.function(_get_plusorminus_diff_amount, string="Difference Amount", type="char"),
        'receive_from':fields.char('Received From'),
        'invoice_total':fields.float('Invoice Total')
        
                 }
    _defaults = {
        'date': fields.datetime.now,
        }        

    def create(self, cursor, user, vals, context=None):
        credit_no = self.pool.get('ir.sequence').get(cursor, user,
            'manual.sales.denomination') or '/'
        vals['name'] = credit_no
        return super(manual_sale_denomination, self).create(cursor, user, vals, context=context)
    
    
    def button_dummy(self, cursor, user, ids, context=None):
        return True
    
    def retrieve_data(self, cursor, user, ids, context=None):
        notes_line = [{'notes':10000, 'note_qty':False}, {'notes':5000, 'note_qty':False}, {'notes':1000, 'note_qty':False}, {'notes':500, 'note_qty':False},{'notes':200, 'note_qty':False}, {'notes':100, 'note_qty':False}, {'notes':50, 'note_qty':False},  {'notes':20, 'note_qty':False},{'notes':10, 'note_qty':False}, {'notes':5, 'note_qty':False},{'notes':1, 'note_qty':False}]                
        notes_line_obj = self.pool.get('manual.sales.denomination.note.line')
        if ids:
            deno_id = ids [0]
            cursor.execute ("delete from manual_sales_denomination_note_line where denomination_note_ids =%s",(deno_id,))
            for ptl in notes_line:
                note_line_res = {                                                            
                  'denomination_note_ids':deno_id,
                  'note_qty':0,
                  'notes':ptl['notes'],
                  'amount':0,
                }
                notes_line_obj.create(cursor, user, note_line_res, context=context)
        return True
manual_sale_denomination()      

class manual_sale_denomination_note_line(osv.osv):    
    _name = 'manual.sales.denomination.note.line'
    
    def on_change_note_qty(self, cr, uid, ids, notes, note_qty, context=None):
        values = {}
        if notes and note_qty:
            notes = notes.replace(',', '')
            values = {
                'amount':float(notes) * note_qty,
            }
        return {'value': values}   
    
    _columns = {
                'denomination_note_ids': fields.many2one('manual.sales.denomination', 'Sales Denomination'),
                'notes':fields.char('Notes', required=True),
                'note_qty':fields.integer('Qty', required=True),
                'amount':fields.float('Total', digits_compute=dp.get_precision('Product Price')),
                }
    _defaults = {
        'amount': 0.0,
        }   
manual_sale_denomination_note_line()       