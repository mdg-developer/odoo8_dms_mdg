from openerp.osv import fields, osv
class tablet_information(osv.osv):
    _name = "tablets.information"
    _description = "Tablet Informations"

    _columns = {
                'name': fields.char('Tablet Name', required=True),
                'type': fields.char('Type', required=True),
                'model': fields.char('Model', required=True),
                'mac_address': fields.char('Tablet ID', required=True),
                'date': fields.date('Date', required=True),
                'note': fields.text('Description'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team', required=True),
                'storage_day': fields.integer('Data Storage', size=4, required=True, help="Help"),
                'hotline': fields.char('Hotline'),
    }
    _defaults = {
               
    }  
tablet_information()
