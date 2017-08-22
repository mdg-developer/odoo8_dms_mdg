from openerp.osv import fields, osv

class stock_location(osv.osv):
    _inherit = "stock.location"
    
        
    _columns = {
               'is_consigment':fields.boolean(' Is a Consigment Location? '),
               'sale_partner_id':fields.many2one('res.partner','Consignee')
               }
