from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools
from datetime import datetime, date, timedelta as td
class customer_rebate(osv.Model):
    "Customer Rebate"
    _name = "customer.rebate"
    _description = __doc__
    _columns = {
        
         'partner_id':fields.many2one('res.partner', 'Customer', ondelete='cascade'),
         'qty':fields.integer('Quantity'),
         'amt':fields.integer('Refund Amount'),
         'date':fields.date('Date'),
         'code':fields.char('Promotion'),
         'remark':fields.text('Remark'),
         'year':fields.char('Year'),
         'product_id':fields.many2one('product.product', string='Product' , required=True),
         'state':fields.selection([('progress', 'Pending'), ('manual', 'Pending') , ('done' , 'Invoiced')], 'Status'),
         'section_id': fields.many2one('crm.case.section', 'Sales Team'),
         'user_id':fields.many2one('res.users', 'Saleman Name'),
         'name': fields.char('Sale Order'),
         'date_order': fields.date('Date'),
         
    }
    
customer_rebate()

class customer_rebate_generate(osv.Model):
    "Customer Rebate Generate"
    _name = "customer.rebate.generate"
    _description = __doc__
    _columns = {
        
         'from_date':fields.date('From Date', required=True),
         'to_date':fields.date('To Date', required=True),
         'year':fields.char('Year', required=True),
    }
    
    def action_generate(self, cr, uid, ids, context=None):
               
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        sale_order_obj = self.pool.get('sale.order')
        rebate_obj = self.pool.get('customer.rebate')
        result = {}
        
        datas = self.read(cr, uid, ids, ['from_date', 'to_date', 'year'], context=None)
        print 'Datas>>>>', datas
        from_date = to_date = year = inv_id = None
        month_year_result = []
        if datas:
            for data in datas:
                from_date = data['from_date']
                to_date = data['to_date']
                year = data['year']  
                d1 = datetime.strptime(from_date, '%Y-%m-%d')
                d2 = datetime.strptime(to_date, '%Y-%m-%d')
                delta = d2 - d1
                for i in range(delta.days + 1):
                    str_date = d1 + td(days=i)
                    only_month = str_date.strftime('%m')
                    only_year = str_date.strftime('%Y')
                    month_year = str(only_month + '-' + only_year)
                    if month_year not in month_year_result:
                        month_year_result.append(month_year)
            print 'month_year_result >>> ', month_year_result
            
            cr.execute("""select customer_id,qty,rebate_amount,promotion,product_id,rebate_date,state,section_id,user_id,name,date_order from customer_rebate_report(%s,%s)""", (from_date, to_date,))
            rebate_result = cr.fetchall()  
            print 'rebate_result date',rebate_result       
            if rebate_result:                
                for val in rebate_result:
                    print 'val[5]',val[5]
                    cr.execute("""select * from customer_rebate where partner_id=%s and qty=%s and amt=%s and code=%s
                                and product_id=%s and date=%s and state=%s and section_id=%s and user_id=%s and name=%s and date_order=%s""", (val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7],val[8],val[9],val[10]))
                    rebate_data = cr.fetchall();
                    print 'rebate_data',rebate_data
                    if not rebate_data:                   
                    # cr.execute("""select id from product_product where name_template=%s""",(val[4],))
                    # product_id=cr.fetchall()
                        data_id = {'partner_id':val[0],
                            'qty':val[1],
                            'amt':val[2],
                            'code':val[3],
                            'product_id':val[4],
                            'date':val[5],
                            'state':val[6],
                            'section_id':val[7],
                            'user_id':val[8],
                            'name':val[9],
                            'date_order':val[10],
                            'year':year, }                            
                        inv_id = rebate_obj.create(cr, uid, data_id, context=context)
                    for details in self.browse(cr, uid, ids, context=context):
                    
                        result[details.id] = inv_id
                
            cust_rebate_list=[]
            cr.execute("""select id from customer_rebate where date between %s and %s""", (from_date,to_date,))
            cust_rebate_data=cr.fetchall()
            print 'cust_rebate_data',cust_rebate_data
            for data in cust_rebate_data:
                for rebate_id in data:
                    print 'rebate_id',rebate_id
                    cust_rebate_list.append(rebate_id)
                    print 'cust_rebate_list',cust_rebate_list
            result = mod_obj.get_object_reference(cr, uid, 'customer_rebate', 'action_customer_rebate_form')          
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = str([('id', 'in',cust_rebate_list)])
            print 'Result >>>>' , result
            cr.execute("""delete from customer_rebate_generate where id=%s""", (ids[0],))
        return result
