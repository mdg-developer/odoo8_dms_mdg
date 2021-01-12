from openerp.osv import orm
from openerp.osv import fields, osv

class warehouse_report_url(osv.osv):
    _name = 'warehouse.report.url'
    _description = 'Warehouse Report URL'
  
    _columns = {
                'url_link':fields.char('URL', size=150, required=True),
                'url_name':fields.char('Report Name', size=150, required=True),
				'local_cloud':fields.selection([('local', 'Local Server'),
                                                ('cloud', 'Cloud Server'),
                                                ('null', ''),
                                               ], 'Local Cloud'),                   
               }
    
    def go_report(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Go to Report',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            user_id = uid
            print user_id
            print record.url_link+'&user_id='+ str(user_id)
            result['url'] = record.url_link+'&user_id='+ str(user_id)
            
        return result

warehouse_report_url()