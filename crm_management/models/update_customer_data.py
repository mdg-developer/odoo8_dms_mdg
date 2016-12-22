import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class partner_update_data(osv.osv):
    _name = 'partner.update.data'
    _description = 'Customer Update Data'
    _columns = {
                'name':fields.char('Description'),
                'partner_id':fields.many2one('res.partner', 'Customer', required=True),
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'),
                'sales_channel':fields.many2one('sale.channel', 'Sale Channel'),
                'demarcation_id': fields.many2one('sale.demarcation', 'Demarcation'),
                'frequency_id':fields.many2one('plan.frequency', 'Frequency'),
                'class_id':fields.many2one('sale.class', 'Class'),
                'chiller_true':fields.boolean('Chiller True'),
                'chiller_false':fields.boolean('Chiller False'),
                'hamper_true':fields.boolean('Hamper True'),
                'hamper_false':fields.boolean('Hamper False'),
                 }
    _defaults = {
        'chiller_true': False,
        'chiller_false': False,
        'hamper_true': False,
        'hamper_false': False,
    }    
    def update_data(self, cr, uid, ids, context=None):  
        partner_obj = self.pool.get('res.partner')
        update_data = self.browse(cr, uid, ids, context=context)
        partner_id = update_data.partner_id.id
        outlet_type = update_data.outlet_type
        sales_channel = update_data.sales_channel
        demarcation_id = update_data.demarcation_id
        frequency_id = update_data.frequency_id
        class_id = update_data.class_id
        chiller_true = update_data.chiller_true
        chiller_false = update_data.chiller_false
        hamper_true = update_data.hamper_true
        hamper_false = update_data.hamper_false        
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
        if chiller_true is True:        
                partner_obj.write(cr, uid, partner_id, {'chiller':True}, context=None)         
        if chiller_false is True:        
                partner_obj.write(cr, uid, partner_id, {'chiller':False}, context=None)               
        if hamper_true is True:        
                partner_obj.write(cr, uid, partner_id, {'hamper':True}, context=None)         
        if hamper_false is True:        
                partner_obj.write(cr, uid, partner_id, {'hamper':False}, context=None)                   
        return True                                                              
