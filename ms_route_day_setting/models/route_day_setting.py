from openerp.osv import fields, osv
from openerp.tools.translate import _

class route_day_setting(osv.osv):
    _name = 'route.day.setting'
    
    def _total_customer_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        partner_count = 0
        if context is None:
            context = {}        
        for data in self.browse(cr, uid, ids, context=context):                       
            partner_count = len(data.p_line)                                            
            res[data.id] = partner_count
        return res  
    
    _columns = {
                'sale_team_id':fields.many2one('crm.case.section', 'Sales Team'),
                'total_customer':fields.function(_total_customer_count, string='Total Customer',type='integer'), 
                'p_line':fields.one2many('route.day.setting.line', 'line_id', 'Customer Lines', copy=True),         
            }
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(route_day_setting, self).write(cr, uid, ids, vals, context=context)
        self.change_sequence(cr, uid, ids, context)
        return res
    
    def change_sequence(self, cr, uid, ids, context=None):
        
        line_obj = self.pool.get('route.day.setting.line')
        seq = 0
        line_no = 0
        prev_row = None
        sequence = None 
        i = 0       
        for data in self.browse(cr, uid, ids, context):
            array_list = data.p_line.sorted(key=lambda r: r.route_day_id.sequence).ids
            for line in data.p_line.sorted(key=lambda r: r.route_day_id.sequence): 
                if i != 0:
                    previous = array_list[i-1]                
                    prev_row = line_obj.browse(cr, uid, previous, context)                    
                    if prev_row:                        
                        if prev_row.route_day_id.sequence != line.route_day_id.sequence:                            
                            seq = 0
                i = i + 1
                seq = seq + 1
                line_no = line_no + 1    
                if line.route_day_id.sequence:
                    sequence = str(line.route_day_id.sequence) + str("%03d" % (seq,))
                line_obj.write(cr, uid, [line.id], {'line_no': line_no,
                                                    'seq': sequence}, context=context)  
                   
    def retrieve_data(self, cr, uid, ids, context=None):
        
        customer_obj = self.pool.get('res.partner')
        route_day_line_obj = self.pool.get('route.day.setting.line')
        plan_setting = self.browse(cr, uid, ids, context=context)
        cr.execute("delete from route_day_setting_line where line_id=%s",(plan_setting.id,)) 
        if plan_setting.sale_team_id:      
            partner_ids = customer_obj.search(cr, uid, [('section_id.id', '=', plan_setting.sale_team_id.id),('customer','=',True)], order='township', context=context)
            if partner_ids:                
                for partner_id in partner_ids:
                    partner = customer_obj.browse(cr, uid, partner_id, context=context)
                    line = route_day_line_obj.search(cr, uid, [('partner_id', '=', partner.id),('line_id', '=', plan_setting.id)], context=context)
                    if not line:
                        values = {
                                    'line_id': plan_setting.id,
                                    'partner_id': partner.id,
                                    'township_id': partner.township.id if partner.township else None,
                                    'street': partner.street, 
                                }
                        route_day_line_obj.create(cr, uid, values, context=context)
                
    def refresh_new_customer(self, cr, uid, ids, context=None):
        
        customer_obj = self.pool.get('res.partner')
        route_day_line_obj = self.pool.get('route.day.setting.line')
        plan_setting = self.browse(cr, uid, ids, context=context)
        if plan_setting.sale_team_id:
            partner_ids = customer_obj.search(cr, uid, [('section_id.id', '=', plan_setting.sale_team_id.id),('customer','=',True)], order='township', context=context)
            if partner_ids:                
                for partner_id in partner_ids:
                    partner = customer_obj.browse(cr, uid, partner_id, context=context)
                    line = route_day_line_obj.search(cr, uid, [('partner_id', '=', partner.id),('line_id', '=', plan_setting.id)], context=context)
                    if not line:
                        values = {
                                'line_id': plan_setting.id,
                                'partner_id': partner.id,
                                'township_id': partner.township.id if partner.township else None,
                                'street': partner.street, 
                            }
                        route_day_line_obj.create(cr, uid, values, context=context)
                        
class route_day_setting_line(osv.osv):  
    _name = 'route.day.setting.line'
    _order = 'seq,township_name'
    
    def _total_day_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        route_day_line_obj = self.pool.get('route.day.setting.line')
        if context is None:
            context = {}        
        for data in self.browse(cr, uid, ids, context=context):                       
            day_count = route_day_line_obj.search_count(cr, uid, [('line_id', '=', data.line_id.id),('route_day_id', '=', data.route_day_id.id)], context=context)                                         
            res[data.id] = day_count
        return res  
    
    _columns = {                
                'line_id':fields.many2one('route.day.setting', 'Line', ondelete='cascade', select=True),
                'line_no':fields.integer('No'),
                'partner_id': fields.many2one('res.partner', 'Customer Name'),
                'township_id': fields.many2one('res.township', 'Township'),
                'township_name': fields.char("Township Name", related='township_id.name'),
                'street':fields.char('Street'),
                'route_day_id': fields.many2one('route.day', 'Route Day'),
                'frequency_id':fields.many2one('plan.frequency','Frequency'),
                'seq':fields.char('Sequence'),
                'remark':fields.char('Remark'),
                'day_count':fields.function(_total_day_count, string='Total Day Count',type='integer'), 
                'sequence': fields.integer('Line Sequence'),
            }
    
    def unassign(self, cr, uid, ids, context=None):
        
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ms_route_day_setting', 'view_route_day_unassign_dialog_form')

        data = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Unassign"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'route.day.unassign',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'partner_id': data.partner_id.id,
                'sale_team_id': data.line_id.sale_team_id.id,
            }
        }   
        
    def unlink(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids, context=context):
            setting = data.line_id.id
        res = super(route_day_setting_line, self).unlink(cr, uid, ids, context=context)  
        self.pool.get('route.day.setting').change_sequence(cr, uid, setting, context=None)           
        return res   
        
    