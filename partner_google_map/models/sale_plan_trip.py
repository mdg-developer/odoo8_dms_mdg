from openerp.osv import fields, osv

class sale_plan_trip(osv.osv):
    _inherit = 'sale.plan.trip'
    
    def open_google_map(self, cr, uid, ids, context=None):
        partner_ids = []
        data = self.read(cr, uid, ids, context=context)[0]
        plan_day_line_obj = self.pool.get('sale.plan.day.line')
       
        cr.execute("select distinct partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s",(ids[0],))
        datas = cr.fetchall()
        
        for day_line_id in datas:
            partner_ids.append(day_line_id[0])
        
        if len(partner_ids) > 0:
            return {
                        'type': 'ir.actions.act_url',
                        'url': '/selected_partner_map?id=%s' % partner_ids,
                        'target': 'self',
                    }
    def open_polygon_map(self, cr, uid, ids, context=None):
        partner_ids = []    
        data = self.read(cr, uid, ids, context=context)[0]
        plan_day_line_obj = self.pool.get('sale.plan.day.line')
       
        cr.execute("select distinct partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s",(ids[0],))
        datas = cr.fetchall()
        for day_line_id in datas:
            partner_ids.append(day_line_id[0])
        
        if len(partner_ids) > 0:        
            return {
                'type': 'ir.actions.act_url',
                'url': '/partners_polygon_map?id=%s' % partner_ids,
                'target': 'self',
            }