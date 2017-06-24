'''
Created on Nov 14, 2014

'''

from openerp import tools
from openerp.osv import fields, osv

class stock_different_report(osv.osv):
    _name = "stock.different.report"
    _description = "Stock Different Report"
    _auto = False
    _columns = {
          'product_id':fields.many2one('product.product', 'Product'),
          'return_quantity':fields.integer('Return Qty'),
        'different_qty':fields.integer('Different Qty'),
         'return_date':fields.date('Date'),
         'name':fields.char('SRN NO'),
         'branch_id':fields.many2one('res.branch', 'Branch'),
         'sale_team_id':fields.many2one('crm.case.section', 'Sales Team'),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_different_report')    
        cr.execute("""
            CREATE OR REPLACE VIEW stock_different_report AS (        
                                    select MIN(srl.id) as id,sr.name,srl.product_id,srl.different_qty , CASE WHEN srl.return_quantity >=0  THEN 0 ELSE srl.return_quantity END return_quantity,sr.return_date,sr.sale_team_id,sr.branch_id
                                    from stock_return_line srl 
                                    left join  stock_return sr on srl.line_id=sr.id
                                    where different_qty>0 or return_quantity < 0
                                    and state !='cancel'
                                    group by product_id,return_date,sale_team_id,different_qty,branch_id,return_quantity,name
                                    order by name desc

            )""")