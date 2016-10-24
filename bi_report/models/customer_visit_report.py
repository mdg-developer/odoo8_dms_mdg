
from openerp import tools
from openerp.osv import fields, osv

class customer_visit_report(osv.osv):
    _name = "customer.visit.report"
    _description = "Customer Visit Statistics"
    _auto = False
    _rec_name = 'date'
    _columns = {
           'customer_id':fields.many2one('res.partner', 'Customer', domain="[('customer','=',True)]"),
        'customer_code':fields.char('Customer Code'),
        'user_id':fields.many2one('res.users', 'Salesman Name'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID'),
       'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
       'date':fields.datetime('Date'),
        'visit_reason':fields.selection([
                ('no_shopkeeper', 'No Shopkeeper'),
                ('no_authorized_person', 'No Authorized Person'),
                ('products_already_existed', 'Products Already Existed'),
                 ('sold_other_people_products', 'Sold Other People Products'),
                 ('other_reason', 'Other Reasons')
            ], 'Reason'),
                'other_reason':fields.text('Remark'),
        'm_status':fields.selection([('pending', 'Pending'), ('approved', 'Approved'),
                                                      ('reject', 'Reject')], string='Status'), }
    _order = 'date desc'

    def _select(self):
        select_str = """
              select min(id) AS id,sale_plan_day_id,
              other_reason,
              user_id,
              sale_team_id,
              visit_reason,
              customer_id,
              sale_plan_trip_id,
              customer_code,
              tablet_id,
              date,
              m_status 

        """
        return select_str

    def _from(self):
        from_str = """
                   customer_visit 
                      
                             
        """
        return from_str

    def _group_by(self):
        group_by_str = """
              GROUP BY 
              sale_plan_day_id,
              other_reason,
              user_id,
              sale_team_id,
              visit_reason,
              customer_id,
              sale_plan_trip_id,
              customer_code,
              tablet_id,
              date,
              m_status
                    
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
                       %s
            FROM  %s 
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
