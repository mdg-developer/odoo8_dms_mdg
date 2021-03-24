from openerp.osv import fields, osv
from datetime import datetime

class res_users(osv.osv):
    _inherit = "res.users"
    
    def get_good_issue_note_lists(self, cursor, user, ids, branch_id=None, context=None):
        
        if branch_id:
            cursor.execute('''select id
                            from good_issue_note
                            where state='approve'
                            and branch_id=%s
                            union
                            select id
                            from good_issue_note
                            where state='issue'
                            and issue_date=now()::date''',(branch_id,))
            note_record = cursor.dictfetchall() 
            if note_record:
                return note_record         
            
    def get_stock_balance(self, cursor, user, ids, warehouse_id=None, product_id=None, location_id=None, context=None):
        
        if location_id and not warehouse_id and not product_id:
            cursor.execute('''select loc.complete_name location_name,name_template product_name,sum(quant.qty) total_small_qty,
                            round((sum(quant.qty)/round((1/factor),0))::numeric,0) total_bigger_qty
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and usage='internal'
                            and loc.active=true
                            and loc.id=%s
                            group by loc.complete_name,name_template,uom.factor''',(location_id,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record 
        if warehouse_id and product_id:
            cursor.execute('''select loc.complete_name location_name,name_template product_name,sum(quant.qty) total_small_qty,
                            round((sum(quant.qty)/round((1/factor),0))::numeric,0) total_bigger_qty
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and usage='internal'
                            and loc.active=true
                            and quant.product_id=%s
                            and loc.location_id in (select view_location_id from stock_warehouse where id=%s)
                            group by loc.complete_name,name_template,uom.factor''',(warehouse_id,product_id,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record  
            
    def get_all_locations(self, cursor, user, ids, warehouse_id=None, context=None):   
        
        if warehouse_id:
            cursor.execute('''select id,complete_name as name
                            from stock_location
                            where active=true
                            and usage='internal'
                            and location_id in (select view_location_id from stock_warehouse where id=%s)''',(warehouse_id,))
            data = cursor.dictfetchall() 
            if data:
                return data     
