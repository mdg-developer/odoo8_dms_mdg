import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class partner_update_data(osv.osv_memory):
    _name = 'partner.update.data'
    _description = 'Customer Update Data'
    _columns = {
                'name':fields.char('Description'),
                'partner_id':fields.many2one('res.partner', 'Customer',required=True),
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'),
                'sales_channel':fields.many2one('sale.channel', 'Sale Channel'),
                'demarcation_id': fields.many2one('sale.demarcation', 'Demarcation'),
                'frequency_id':fields.many2one('plan.frequency', 'Frequency'),
                'class_id':fields.many2one('sale.class', 'Class'),
                'chiller':fields.boolean('Chiller'),
    }
    _defaults = {
        'chiller': False,
    }    
    def update_data(self, cr, uid, ids, context=None):  
        partner_obj = self.pool.get('res.partner')
        update_data = self.browse(cr, uid, ids, context=context)
        partner_id=update_data.partner_id.id
        outlet_type=update_data.outlet_type
        sales_channel=update_data.sales_channel
        demarcation_id=update_data.demarcation_id
        frequency_id=update_data.frequency_id
        class_id=update_data.class_id
        chiller=update_data.chiller
        if outlet_type:        
                partner_obj.write(cr, uid, partner_id, {'outlet_type':outlet_type.id}, context=None)
        if sales_channel:        
                partner_obj.write(cr, uid, partner_id, {'sales_channel':sales_channel.id}, context=None)
        if demarcation_id:        
                partner_obj.write(cr, uid, partner_id, {'demarcation_id':demarcation_id.id}, context=None)
        if frequency_id:        
                partner_obj.write(cr, uid, partner_id, {'frequency_id':frequency_id.id}, context=None)
        if class_id:        
                partner_obj.write(cr, uid, partner_id, {'class_id':class_id.id}, context=None)
        if chiller is True:        
                partner_obj.write(cr, uid, partner_id, {'chiller':True}, context=None)          
        return True                                                              