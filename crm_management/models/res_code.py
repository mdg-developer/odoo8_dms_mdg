from openerp.osv import fields, osv

class res_code(osv.osv):
    _name = "res.code"
    _columns = {
               'city_id':fields.many2one('res.city', string='City'),
               'township_id':fields.many2one('res.township', string='Township'),
               'sale_channel_id':fields.many2one('sale.channel', string='Channel'),
               'branch_id':fields.many2one('res.branch', string='Branch'),
               'prefix':fields.char(string='Prefix'),
               'nextnumber':fields.integer(string='Next Number'),
               'padding':fields.integer(string='Padding')
               }
    
    def generateCode(self, cr, uid, ids, context=None):
        code = city = township = sale_channel = nextNumber = padding = updateNumber = None
        if ids:
            for obj in self.browse(cr, uid, ids, context=context):
                city = obj.city_id.code
                township = obj.township_id.code
                sale_channel = obj.sale_channel_id.code
                branch = obj.branch_id.branch_code
                prefix = obj.prefix
                nextNumber = obj.nextnumber
                padding = obj.padding
                code = None
                if branch and township and prefix and nextNumber and padding:
                    code = branch + '-' + township + '.' + prefix
                    result = None
                    while(len(str(nextNumber)) <= padding - 1):
                        nextNumber = '0' + str(nextNumber)
                        result = nextNumber
                    if len(str(nextNumber)) > padding - 1:
                        result = str(nextNumber)
                    code = code + result
                    updateNumber = obj.nextnumber + 1
                    self.write(cr, uid, ids, {'nextnumber':updateNumber}, context=context)
                if branch and township and not prefix and nextNumber and padding:
                    code = branch + '-' + township + '.'
                    result = None
                    while(len(str(nextNumber)) <= padding - 1):
                        nextNumber = '0' + str(nextNumber)
                        result = nextNumber
                    if len(str(nextNumber)) > padding - 1:
                        result = str(nextNumber)
                    code = code + result
                    updateNumber = obj.nextnumber + 1
                    self.write(cr, uid, ids, {'nextnumber':updateNumber}, context=context)
        return code
        
    
res_code()
