from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _
TIME_SELECTION = [
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
         ('09', '09'),
         ('10', '10'),
         ('11', '11'),
        ('12', '12'),
         ('13', '13'),
         ('14', '14'),
          ('15', '15'),
          ('16', '16'),
         ('17', '17'),
         ('18', '18'),
         ('19', '19'),
         ('20', '10'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
        ('24', '24'),
    ]

class MergePartnerAutomatic(osv.osv):
    _inherit = "base.partner.merge.automatic.wizard"
    _columns = {    
                'customer_code': fields.char(string='Destination Contact Code'),

}
    
    
    def onchange_dst_partner_id(self, cr, uid, ids, dst_partner_id, context=None):
        partner_obj = self.pool.get('res.partner')
        customer_code = False        
        if dst_partner_id:
            customer_id = partner_obj.browse(cr, uid, dst_partner_id, context=context)
            customer_code = customer_id.customer_code         
        return {'value': {'customer_code': customer_code}}    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(MergePartnerAutomatic, self).default_get(cr, uid, fields, context)
        if context.get('active_model') == 'res.partner' and context.get('active_ids'):
            partner_ids = context['active_ids']
            res['state'] = 'selection'
            res['partner_ids'] = partner_ids
            res['dst_partner_id'] = self._get_ordered_partner(cr, uid, partner_ids, context=context)[-1].id
            res['customer_code'] =self._get_ordered_partner(cr, uid, partner_ids, context=context)[-1].customer_code
        return res    
    
class res_partner(osv.osv):
    _inherit = "res.partner"
       
    def customer_target(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        wiz_view = mod_obj.get_object_reference(cr, uid, 'customer_calling_card', 'view_customer_target_form')
        for move in self.browse(cr, uid, ids, context=context):
            ctx = {
                'partner_id': move.id,
                
            }
            #customer.target.form
            target = self.pool.get('customer.target').search(cr,uid,[('partner_id','=',move.id)],limit=1,order='id desc')
            if target:
                return {
                'type': 'ir.actions.act_window',
                'name': _('Customer Target'),
                'res_model': 'customer.target',
                'res_id': target[0], #If you want to go on perticuler record then you can use res_id 
    
                'context': ctx,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [wiz_view[1]],
                'target': 'current',
                'nodestroy': True,
            }
            else:    
                act_import = {
                    'name': _('Customer Target'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'customer.target',
                    'view_id': [wiz_view[1]],
                    'nodestroy': True,
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                    'context': ctx,
                }
                return act_import
