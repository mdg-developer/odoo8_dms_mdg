from openerp.osv import fields, osv

class route_day_unassign(osv.osv):
    _name = 'route.day.unassign'
    
    def unassign(self, cr, uid, ids, context=None):
        
        if context.get('sale_team_id') and context.get('partner_id'):
            sale_team = context.get('sale_team_id')
            sale_team_obj = self.pool.get('crm.case.section').browse(cr, uid, sale_team, context=context)
            partner = context.get('partner_id')
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
            day_setting_obj = self.pool.get('route.day.setting')
            day_setting_line_obj = self.pool.get('route.day.setting.line')
            for team in sale_team_obj.related_sales_team_ids:
                day_setting = day_setting_obj.search(cr, uid, [('sale_team_id', '=', team.id)], context=context)
                if day_setting:
                    setting = day_setting_obj.browse(cr, uid, day_setting, context=context)
                    day_setting_line = day_setting_line_obj.search(cr, uid, [('line_id', '=', setting.id),
                                                                             ('partner_id', '=', partner_obj.id)], context=context)
                    if day_setting_line:                
                        line = day_setting_line_obj.browse(cr, uid, day_setting_line, context=context)
                        line.unlink()   
                                  
            