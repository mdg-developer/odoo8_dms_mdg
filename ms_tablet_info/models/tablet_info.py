from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
class tablet_information(osv.osv):
    _name = "tablets.information"
    _description = "Tablet Informations"

    _columns = {
                'name': fields.char('Tablet Name', required=True),
                'type': fields.char('Type', required=True),
                'model': fields.char('Model', required=True),
                'mac_address': fields.char('Tablet ID', required=True),
                'token':fields.char("FCM Token"),
                'date': fields.date('Date', required=True),
                'note': fields.text('Description'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team', required=True),
                'storage_day': fields.integer('Data Storage', size=4, required=True, help="Help"),
                'hotline': fields.char('Hotline'),
                'device_id': fields.char('Device ID'),
                'is_testing': fields.boolean('Is Testing'),
                'branch_id':fields.many2one('res.branch', 'Branch'),
    }
    _defaults = {
               'is_testing' : False,
    }  
    
    def check_device_id(self, cr, uid, device_id , tablet_name, context=None, **kwargs):    
        try:
           cr.execute('''
           select device_id from tablets_information where name = %s
           ''', (tablet_name,))
           datas = cr.fetchall()
           if datas:
               try:
                   device_imei = datas[0][0]
               except Exception, e:
                   device_imei = datas[0]
               if device_imei:
                   if long(device_imei) == device_id:
                       return True
                   else:
                       return False
               else:
                   return True                          
        except Exception, e:
           print 'False check device Id Error >>>>', e
           return False
            
    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            mac_address = context.get('mac_address', True) and d.get('mac_address', False) or False
            if mac_address:
                name = '%s' % (mac_address)
            return (d['id'], name)

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for val in self.browse(cr, SUPERUSER_ID, ids, context=context):
           if val:
               name = "%s" % (val.mac_address) or val.name

           mydict = {
                      'id': val.id,
                      'name': name,
                      }
          # print' mydict',mydict
           result.append(_name_get(mydict))
        return result
tablet_information()
