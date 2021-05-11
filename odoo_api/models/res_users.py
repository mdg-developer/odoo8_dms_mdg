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
                            and branch_id=%s
                            and issue_date=now()::date''',(branch_id,branch_id,))
            note_record = cursor.dictfetchall() 
            if note_record:
                return note_record         
            
    def get_stock_balance(self, cursor, user, ids, warehouse_id=None, product_id=None, location_id=None, context=None):
        
        if location_id and not warehouse_id and not product_id:
            cursor.execute('''select loc.name location_name,name_template product_name,sum(quant.qty) total_small_qty,
                            round((sum(quant.qty)/(1/factor))::numeric,1) total_bigger_qty,
                            (select uom.name from product_uom uom where uom.id=pt.uom_id) small_uom,
                            (select uom.name from product_uom uom where uom.id=pt.report_uom_id) bigger_uom
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and usage='internal'
                            and loc.active=true
                            and pp.active=true
                            and pt.active=true
                            and loc.id=%s
                            group by loc.name,name_template,uom.factor,pp.sequence,pt.uom_id,pt.report_uom_id
                            order by pp.sequence''',(location_id,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record 
        if warehouse_id and product_id:
            cursor.execute('''select loc.name location_name,name_template product_name,sum(quant.qty) total_small_qty,
                            round((sum(quant.qty)/(1/factor))::numeric,1) total_bigger_qty,
                            (select uom.name from product_uom uom where uom.id=pt.uom_id) small_uom,
                            (select uom.name from product_uom uom where uom.id=pt.report_uom_id) bigger_uom
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and usage='internal'
                            and loc.active=true
                            and pp.active=true
                            and pt.active=true
                            and quant.product_id=%s
                            and loc.location_id in (select view_location_id from stock_warehouse where id=%s)
                            group by loc.name,name_template,uom.factor,pp.sequence,pt.uom_id,pt.report_uom_id
                            order by pp.sequence''',(product_id,warehouse_id,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record  
            
    def search_product_in_stock_lookup(self, cursor, user, ids, location_id=None, product_name=None, barcode_no=None, context=None):
            
        if location_id and product_name:
            param_product_name = '%' + product_name.lower() + '%'
            cursor.execute('''select loc.name location_name,name_template product_name,sum(quant.qty) total_small_qty,
                            round((sum(quant.qty)/(1/factor))::numeric,1) total_bigger_qty,
                            (select uom.name from product_uom uom where uom.id=pt.uom_id) small_uom,
                            (select uom.name from product_uom uom where uom.id=pt.report_uom_id) bigger_uom
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and usage='internal'
                            and loc.active=true
                            and pp.active=true
                            and pt.active=true
                            and loc.id=%s
                            and pp.id in (select id from product_product where lower(name_template) like %s)
                            group by loc.name,name_template,uom.factor,pt.uom_id,pt.report_uom_id''',(location_id,param_product_name,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record 
        if location_id and barcode_no:
            cursor.execute('''select loc.name location_name,name_template product_name,sum(quant.qty) total_small_qty,
                            round((sum(quant.qty)/(1/factor))::numeric,1) total_bigger_qty,
                            (select uom.name from product_uom uom where uom.id=pt.uom_id) small_uom,
                            (select uom.name from product_uom uom where uom.id=pt.report_uom_id) bigger_uom
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom,product_multi_barcode barcode
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and pt.id=barcode.product_tmpl_id
                            and usage='internal'
                            and loc.active=true
                            and pp.active=true
                            and pt.active=true
                            and loc.id=%s
                            and barcode.name=%s
                            group by loc.name,name_template,uom.factor,pt.uom_id,pt.report_uom_id''',(location_id,barcode_no,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record
            
    def get_all_locations(self, cursor, user, ids, warehouse_id=None, context=None):   
        
        if warehouse_id:
            cursor.execute('''select id,name
                            from stock_location
                            where active=true
                            and usage='internal'
                            and location_id in (select view_location_id from stock_warehouse where id=%s)''',(warehouse_id,))
            data = cursor.dictfetchall() 
            if data:
                return data 
        
    def search_location(self, cursor, user, ids, warehouse_id=None, location_name=None, context=None):   
        
        if warehouse_id and location_name:
            param_location_name = '%' + location_name.lower() + '%'
            cursor.execute('''select id,name
                            from stock_location
                            where active=true
                            and usage='internal'
                            and location_id in (select view_location_id from stock_warehouse where id=%s)
                            and id in (select id from stock_location where lower(name) like %s)''',(warehouse_id,param_location_name,))
            data = cursor.dictfetchall() 
            if data:
                return data    
            
    def get_good_issue_note_by_sales_team(self, cursor, user, ids, branch_id=None, sales_team=None, from_date=None, to_date=None, context=None):
        
        if branch_id and sales_team and from_date and to_date:
            param_sale_team = '%' + sales_team.lower() + '%'
            cursor.execute('''select id
                            from good_issue_note
                            where state='approve'
                            and branch_id=%s
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            and issue_date between %s and %s
                            union
                            select id
                            from good_issue_note
                            where state='issue'
                            and branch_id=%s
                            and issue_date=now()::date
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            and issue_date between %s and %s''',(branch_id,param_sale_team,from_date,to_date,branch_id,param_sale_team,from_date,to_date,))
            note_record = cursor.dictfetchall() 
            if note_record:
                return note_record 
        if branch_id and not sales_team and from_date and to_date:
            cursor.execute('''select id
                            from good_issue_note
                            where state='approve'
                            and branch_id=%s                            
                            and issue_date between %s and %s
                            union
                            select id
                            from good_issue_note
                            where state='issue'
                            and branch_id=%s
                            and issue_date=now()::date                            
                            and issue_date between %s and %s''',(branch_id,from_date,to_date,branch_id,from_date,to_date,))
            note_record = cursor.dictfetchall() 
            if note_record:
                return note_record
        if branch_id and sales_team and not from_date and not to_date:
            param_sale_team = '%' + sales_team.lower() + '%'
            cursor.execute('''select id
                            from good_issue_note
                            where state='approve'
                            and branch_id=%s
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            union
                            select id
                            from good_issue_note
                            where state='issue'
                            and branch_id=%s
                            and issue_date=now()::date
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)''',(branch_id,param_sale_team,branch_id,param_sale_team,))
            note_record = cursor.dictfetchall() 
            if note_record:
                return note_record  
            
    def get_stock_return_lists(self, cursor, user, ids, branch_id=None, context=None):
        
        if branch_id:
            cursor.execute('''select id
                            from stock_return
                            where state='draft'
                            and branch_id=%s
                            union
                            select id
                            from stock_return
                            where state='received'
                            and branch_id=%s
                            and now()::date between return_date and to_return_date''',(branch_id,branch_id,))
            return_record = cursor.dictfetchall() 
            if return_record:
                return return_record   
            
    def get_stock_return_by_sales_team(self, cursor, user, ids, branch_id=None, sales_team=None, from_date=None, to_date=None, context=None):
                
        if branch_id and sales_team and from_date and to_date:
            param_sale_team = '%' + sales_team.lower() + '%'
            cursor.execute('''select id
                            from stock_return
                            where state='draft'
                            and branch_id=%s
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            and (return_date between %s and %s and to_return_date between %s and %s)
                            union
                            select id
                            from stock_return
                            where state='received'
                            and branch_id=%s
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            and now()::date between return_date and to_return_date
                            and (return_date between %s and %s and to_return_date between %s and %s)''',(branch_id,param_sale_team,from_date,to_date,from_date,to_date,branch_id,param_sale_team,from_date,to_date,from_date,to_date,))
            return_record = cursor.dictfetchall() 
            if return_record:
                return return_record   
        if branch_id and not sales_team and from_date and to_date:
            cursor.execute('''select id
                            from stock_return
                            where state='draft'
                            and branch_id=%s
                            and (return_date between %s and %s and to_return_date between %s and %s)
                            union
                            select id
                            from stock_return
                            where state='received'
                            and branch_id=%s
                            and now()::date between return_date and to_return_date
                            and (return_date between %s and %s and to_return_date between %s and %s)''',(branch_id,from_date,to_date,from_date,to_date,branch_id,from_date,to_date,from_date,to_date,))
            return_record = cursor.dictfetchall() 
            if return_record:
                return return_record
        if branch_id and sales_team and not from_date and not to_date:
            param_sale_team = '%' + sales_team.lower() + '%'
            cursor.execute('''select id
                            from stock_return
                            where state='draft'
                            and branch_id=%s
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            union
                            select id
                            from stock_return
                            where state='received'
                            and branch_id=%s
                            and sale_team_id in (select id from crm_case_section where lower(name) like %s)
                            and now()::date between return_date and to_return_date''',(branch_id,param_sale_team,branch_id,param_sale_team,))
            return_record = cursor.dictfetchall() 
            if return_record:
                return return_record     
            
    def get_goods_receipt_lists(self, cursor, user, ids, branch_id=None, context=None):
        
        if branch_id:
            cursor.execute('''select id
                            from branch_good_issue_note
                            where state='issue'
                            and branch_id=%s
                            union
                            select id
                            from branch_good_issue_note
                            where state='receive'
                            and branch_id=%s
                            and receive_date=now()::date''',(branch_id,branch_id,))
            data = cursor.dictfetchall() 
            if data:
                return data   
            
    def search_goods_receipt(self, cursor, user, ids, branch_id=None, from_date=None, to_date=None, context=None):
        
        if branch_id and from_date and to_date:
            cursor.execute('''select id
                            from branch_good_issue_note
                            where state='issue'
                            and branch_id=%s
                            and receive_date between %s and %s
                            union
                            select id
                            from branch_good_issue_note
                            where state='receive'
                            and branch_id=%s
                            and receive_date=now()::date
                            and receive_date between %s and %s''',(branch_id,from_date,to_date,branch_id,from_date,to_date,))
            data = cursor.dictfetchall() 
            if data:
                return data    
            
    def get_stock_transfer_lists(self, cursor, user, ids, context=None):
        
        cursor.execute('''select id
                        from stock_picking
                        where state in ('draft','assigned')
                        and picking_type_id in (select id from stock_picking_type where code='internal')
                        union
                        select id
                        from stock_picking
                        where state='done'
                        and picking_type_id in (select id from stock_picking_type where code='internal')
                        and ((date_done at time zone 'utc' )at time zone 'asia/rangoon')::date=now()::date''')
        data = cursor.dictfetchall() 
        if data:
            return data    
        
    def search_stock_transfer(self, cursor, user, ids, from_date=None, to_date=None, context=None):
        
        if from_date and to_date:
            cursor.execute('''select id
                            from stock_picking
                            where state in ('draft','assigned')
                            and picking_type_id in (select id from stock_picking_type where code='internal')
                            union
                            select id
                            from stock_picking
                            where state='done'
                            and picking_type_id in (select id from stock_picking_type where code='internal')
                            and ((date_done at time zone 'utc' )at time zone 'asia/rangoon')::date between %s and %s''',(from_date,to_date,))
            data = cursor.dictfetchall() 
            if data:
                return data   
            
    def get_inventory_count_lists(self, cursor, user, ids, branch_id=None, context=None):
                     
        if branch_id:   
            cursor.execute('''select id
                            from stock_inventory
                            where state in ('draft','confirm')
                            and location_id in (
                                                    select loc.id
                                                    from stock_location loc,stock_warehouse sw,res_branch rb
                                                    where loc.location_id=sw.view_location_id
                                                    and sw.id=rb.branch_warehouse_id
                                                    and rb.id=%s
                                                );''',(branch_id,))
            data = cursor.dictfetchall() 
            if data:
                return data  
        
    def create_inventory_adjustment(self, cursor, user, ids, location_id=None, date=None, subject=None, inventory_of=None, context=None):
        
        if location_id and date and subject and inventory_of:
            inventory_obj = self.pool.get('stock.inventory')
            inventory_line_obj = self.pool.get('stock.inventory.line')
            values = {                                                            
                        'location_id': location_id,
                        'date': date,
                        'subject': subject,
                        'inventory_of': inventory_of,
                    }
            inventory_id = inventory_obj.create(cursor, user, values, context=context)
            inventory = inventory_obj.browse(cursor, user, inventory_id, context=context)
            inventory.prepare_inventory()
            if inventory_of == 'none':
                inventory_lines = inventory_line_obj.search(cursor, user, [('inventory_id', '=', inventory_id)],context=context)
                if inventory_lines:
                    return inventory_lines.ids
        
    def get_product_count(self, cursor, user, ids, context=None):
        
        product_type = 'product'
        cursor.execute('''select count(pp.*)
                        from product_product pp,product_template pt
                        where pp.product_tmpl_id=pt.id
                        and pp.active=true
                        and pt.active=true
                        and type=%s;''',(product_type,))
        data = cursor.fetchall() 
        if data:
            return data[0][0]   
        
    def add_product_in_stock_transfer(self, cursor, user, ids, picking_id=None, product_id=None, qty=None, uom_id=None, context=None):
        
        if picking_id and product_id and qty and uom_id:
            product = self.pool.get('product.product').browse(cursor, user, product_id, context=context)
            picking = self.pool.get('stock.picking').browse(cursor, user, picking_id, context=context)
            values = {                                                            
                        'picking_id': picking_id,
                        'product_id': product_id,
                        'product_uom_qty': qty,
                        'product_uom': uom_id,
                        'name': product.name_template,
                        'location_id': picking.picking_type_id.default_location_src_id.id,
                        'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
                    }
            stock_move = self.pool.get('stock.move').create(cursor, user, values, context=context)
            return stock_move
        
    def get_internal_locations(self, cursor, user, ids, branch_id=None, context=None):
        
        if branch_id:
            cursor.execute('''select id
                            from stock_location
                            where location_id in (  select view_location_id
                                                    from res_branch rb,stock_warehouse sw
                                                    where rb.branch_warehouse_id=sw.id
                                                    and rb.id=%s)
                            and active=true
                            and usage='internal';''',(branch_id,))
            data = cursor.dictfetchall() 
            if data:
                return data
            
    def get_product_balance(self, cursor, user, ids, product_id=None, location_id=None, context=None):          
            
        if product_id and location_id:
            cursor.execute('''select sum(quant.qty) theoretical_qty,
                            round((sum(quant.qty)/(1/factor))::numeric,1) bigger_qty,
                            (select uom.name from product_uom uom where uom.id=pt.report_uom_id) bigger_uom
                            from stock_quant quant,product_product pp,stock_location loc,product_template pt,product_uom uom
                            where quant.product_id=pp.id
                            and quant.location_id=loc.id
                            and pp.product_tmpl_id=pt.id
                            and pt.report_uom_id=uom.id
                            and usage='internal'
                            and loc.active=true
                            and pp.active=true
                            and pt.active=true
                            and quant.product_id=%s
                            and quant.location_id=%s
                            group by uom.factor,pt.report_uom_id''',(product_id,location_id,))
            balance_record = cursor.dictfetchall() 
            if balance_record:
                return balance_record
            
    def get_product_uom(self, cursor, user, ids, product_id=None, context=None):          
            
        if product_id:
            cursor.execute('''select product_uom_id id
                            from product_template_product_uom_rel rel,product_product pp 
                            where rel.product_template_id=pp.product_tmpl_id
                            and pp.id=%s;''',(product_id,))
            data = cursor.dictfetchall() 
            if data:
                return data
            
    def scan_product_barcode_in_good_issue(self, cursor, user, ids, stock_issue_id=None, barcode_no=None, context=None):
        
        if stock_issue_id and barcode_no:
            cursor.execute('''select line.id
                            from good_issue_note_line line,product_product pp,product_multi_barcode barcode
                            where line.product_id=pp.id
                            and pp.product_tmpl_id=barcode.product_tmpl_id
                            and line_id=%s
                            and barcode.name=%s''',(stock_issue_id,barcode_no,))
            data = cursor.dictfetchall() 
            if data:
                return data   
            
    def scan_product_barcode_in_stock_return(self, cursor, user, ids, stock_return_id=None, barcode_no=None, context=None):
        
        if stock_return_id and barcode_no:
            cursor.execute('''select line.id
                            from stock_return_line line,product_product pp,product_multi_barcode barcode
                            where line.product_id=pp.id
                            and pp.product_tmpl_id=barcode.product_tmpl_id
                            and line_id=%s
                            and barcode.name=%s''',(stock_return_id,barcode_no,))
            data = cursor.dictfetchall() 
            if data:
                return data 
            
    def scan_product_barcode_in_goods_receipt(self, cursor, user, ids, goods_receipt_id=None, barcode_no=None, context=None):
        
        if goods_receipt_id and barcode_no:
            cursor.execute('''select line.id
                            from branch_good_issue_note_line line,product_product pp,product_multi_barcode barcode
                            where line.product_id=pp.id
                            and pp.product_tmpl_id=barcode.product_tmpl_id
                            and line_id=%s
                            and barcode.name=%s''',(goods_receipt_id,barcode_no,))
            data = cursor.dictfetchall() 
            if data:
                return data    
            
    def scan_product_barcode_in_stock_transfer(self, cursor, user, ids, stock_transfer_id=None, barcode_no=None, context=None):
        
        if stock_transfer_id and barcode_no:
            cursor.execute('''select sm.id
                            from stock_move sm,product_product pp,product_multi_barcode barcode
                            where sm.product_id=pp.id
                            and pp.product_tmpl_id=barcode.product_tmpl_id
                            and picking_id=%s
                            and barcode.name=%s''',(stock_transfer_id,barcode_no,))
            data = cursor.dictfetchall() 
            if data:
                return data 
            
    def scan_product_barcode_in_inventory_count(self, cursor, user, ids, inventory_id=None, barcode_no=None, context=None):
        
        if inventory_id and barcode_no:
            cursor.execute('''select line.id
                            from stock_inventory_line line,product_product pp,product_multi_barcode barcode
                            where line.product_id=pp.id
                            and pp.product_tmpl_id=barcode.product_tmpl_id
                            and inventory_id=%s
                            and barcode.name=%s''',(inventory_id,barcode_no,))
            data = cursor.dictfetchall() 
            if data:
                return data   
        