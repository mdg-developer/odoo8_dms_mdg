'''
Created on Nov 14, 2014

'''

from openerp import tools
from openerp.osv import fields, osv

class category_sku_report(osv.osv):
    _name = "category.sku.report"
    _description = "Category Distribution Report"
    _auto = False
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'categ_count':fields.float('Category Count'),
        'categ_id':fields.many2one('product.category', 'Category Name'),
       # 'date':fields.date('Date'),
         'branch_id':fields.many2one('res.branch', 'Branch'),
         'section_id':fields.many2one('crm.case.section', 'Sales Team'),
    }
    
    def _select(self):
        select_str = """
              SELECT min(av.id) as id,av.partner_id,av.section_id,pt.categ_id,av.branch_id,case when count(pt.categ_id) >=1 then 1 else 0 end as categ_count
        """
        return select_str

    def _from(self):
        from_str = """                        
                       account_invoice_line avl
                      join account_invoice av on (avl.invoice_id=av.id) 
                      left join product_product pp on (avl.product_id=pp.id)
                          left join product_template pt on (pp.product_tmpl_id=pt.id)
                            left join res_partner r on (av.partner_id = r.id)
                            left join crm_case_section cs on (cs.id =av.section_id)     
                               """
        return from_str

    def _group_by(self):
        group_by_str = """
                    group by av.partner_id,pt.categ_id,av.branch_id,av.section_id
                    
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