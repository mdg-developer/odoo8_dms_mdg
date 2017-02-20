from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import tools
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
import datetime
class sale_target(osv.osv):
    
    _name = "sales.target"
    _description = "Sales Target"
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        values = {}
        data_line = []
        if sale_team_id:
            sale_team = self.pool.get('crm.case.section').browse(cr, uid, sale_team_id, context=context)
            product_line = sale_team.product_ids
            print 'product_line ', product_line
            for line in product_line:
                print 'product_line ', line
                product = self.pool.get('product.product').browse(cr, uid, line.id, context=context)
                data_line.append({'product_id':line.id,
                                     'product_uom': product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
                                    'price_unit': product.product_tmpl_id.big_list_price,
                                    'product_uom_qty':0.0,
                                              })
            values = {
                'target_line': data_line,
            }
        return {'value': values}
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            for line in order.target_line:
                val1 += line.price_subtotal
                print 'valsssss', val1
            res[order.id] = val1
        return res
    
    def _default_date(self, cr, uid, ids, context=None):
        now = datetime.datetime.now()
        year=now.year
        month=now.month
        return time.strftime('%Y-%m-01')

      
    _columns = {
        'name': fields.char('Description'),
        'branch_id': fields.many2one('res.branch', 'Branch'),
        'month': fields.selection([
                ('01', 'January'),
                ('02', 'February'),
                ('03', 'March'),
                ('04', 'April'),
                ('05', 'May'),
                ('06', 'June'),
                ('07', 'July'),
                ('08', 'August'),
                ('09', 'September'),
                ('10', 'October'),
                ('11', 'November'),
                ('12', 'December'),

            ], 'Month', copy=False, select=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
        'target_line':fields.one2many('sales.target.line', 'sale_ids', string='Sale Target Line', copy=True),
         'description':fields.text('Description'),
         'date':fields.date('Target Date'),
         'year':fields.char('Year'),
       'amount_total': fields.function(_amount_all, string='Total Value', digits_compute=dp.get_precision('Product Price'), store=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
  }
    _defaults = {
        'branch_id': _get_default_branch,
        'date':_default_date,
        'month' : lambda *a: str(time.strftime('%m')),
        'year' : lambda *a: str(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'sales.target',context=context),
        
        }        
sale_target()


class sale_target_line(osv.osv):    
    _name = 'sales.target.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.product_uom_qty
            res[line.id] = price
        return res        
    
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'product_uom': product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
                'price_unit': product.product_tmpl_id.list_price,
            }
        return {'value': values}
    
    def on_change_product_uom_qty(self, cr, uid, ids, product_id, product_uom_qty, context=None):
        values = {}
        if product_uom_qty:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                'price_subtotal':product_uom_qty * product.product_tmpl_id.list_price,
            }
        return {'value': values}   
    
    _columns = {
                'sale_ids': fields.many2one('sales.target', 'Sales Target'),
                'product_id':fields.many2one('product.product', 'Product SKU', required=True),
                'product_uom':fields.many2one('product.uom', 'UoM', readonly=True),
                'product_uom_qty':fields.integer('QTY', required=True),
                 'price_unit': fields.float('Unit Price', required=True, readonly=True, digits_compute=dp.get_precision('Product Price')),
                'price_subtotal': fields.function(_amount_line, string='Amount', digits_compute=dp.get_precision('Product Price'), type='float',),
                'distribution_price': fields.integer('Distribution'),
                
                }
sale_target_line()    

 
class sale_target_report(osv.osv):
    _name = "sale.target.report"
    _description = "Sale Target Statistics"
    _auto = False
    _rec_name = 'date'
    
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
            
    _columns = {
   'branch_id': fields.many2one('res.branch', 'Branch'),
        'month': fields.selection([
                ('01', 'January'),
                ('02', 'February'),
                ('03', 'March'),
                ('04', 'April'),
                ('05', 'May'),
                ('06', 'June'),
                ('07', 'July'),
                ('08', 'August'),
                ('09', 'September'),
                ('10', 'October'),
                ('11', 'November'),
                ('12', 'December'),

            ], 'Month', copy=False, select=True),
                'product_id':fields.many2one('product.product', 'Product SKU', required=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
        'target_line':fields.one2many('sales.target.line', 'sale_ids', string='Sale Target Line', copy=True),
         'description':fields.text('Description'),
         'date':fields.date('Target Date'),
         'year':fields.integer('Year'),
         'product_uom':fields.many2one('product.uom', 'UOM', required=True),
                'product_uom_qty':fields.integer('QTY', required=True),
                 'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Product Price')),
                 'amount_total': fields.float('Total Value', required=True, digits_compute=dp.get_precision('Product Price')),
        #        'price_sub_total': fields.float('Subtotal', required=True, digits_compute=dp.get_precision('Product Price')),
                'price_sub_total': fields.function(_compute_price, string='Subtotal', digits_compute=dp.get_precision('Product Price'), type='float',store=True, readonly=True),


              }
    _order = 'date desc'
 
    def _select(self):
        select_str = """
            select min(st.id) AS id,
               st.sale_team_id,
               st.branch_id,
               stl.product_id,
               u.id as product_uom,
               stl.product_uom_qty,
               st.amount_total,
               stl.price_unit,
               stl.product_uom_qty * stl.price_unit as price_sub_total,
               st.date,
               st.month,
               st.year 
        """
        return select_str
 
    def _from(self):
        from_str = """
                    sales_target st
                   left join sales_target_line stl on (st.id=stl.sale_ids)
                   left join product_uom u on (u.id= stl.product_uom)
        """
        return from_str
 
    def _group_by(self):
        group_by_str = """
                GROUP BY   product_id,
             sale_team_id,
             month,
             amount_total,
             price_unit,
             date,
             year,branch_id,
             u.id,product_uom_qty
                     
        """
        return group_by_str
 
    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


