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
class res_partner(osv.osv):
    _inherit = "res.partner"
       
    def customer_target(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        wiz_view = mod_obj.get_object_reference(cr, uid, 'customer_calling_card', 'customer_target_view')
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
