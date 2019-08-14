from openerp.osv import fields, osv

class sale_plan_day(osv.osv):
    _inherit = 'sale.plan.day'
    
    def open_google_map(self, cr, uid, ids, context=None):
        partner_ids = []
        data = self.read(cr, uid, ids, context=context)[0]
        plan_day_line_obj = self.pool.get('sale.plan.day.line')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        line_ids = plan_day_line_obj.search(cr, uid, [('line_id', 'in', ids)])
        for day_line_id in plan_day_line_obj.browse(cr,uid,line_ids,context=context):
            partner_ids.append(day_line_id.partner_id.id)
        
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
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        line_ids = plan_day_line_obj.search(cr, uid, [('line_id', 'in', ids)])
        for day_line_id in plan_day_line_obj.browse(cr,uid,line_ids,context=context):
            partner_ids.append(day_line_id.partner_id.id)
        
        if len(partner_ids) > 0:        
            return {
                'type': 'ir.actions.act_url',
                'url': '/partners_polygon_map?id=%s' % partner_ids,
                'target': 'self',
            }