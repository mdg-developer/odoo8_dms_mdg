from openerp.osv import fields, osv

class res_code(osv.osv):
    _name = "res.code"
    _columns = {
               'city_id':fields.many2one('res.city', string='City'),
               'township_id':fields.many2one('res.township', string='Township'),
               'branch_id':fields.many2one('res.branch', string='Branch'),
               'nextnumber':fields.integer(string='Next Number'),
               'padding':fields.integer(string='Padding')
               }
    
    def generateCode(self, cr, uid, ids, context=None):
        code = city = township = branch_id = nextNumber = padding = updateNumber = None
        if ids:
            for obj in self.browse(cr, uid, ids, context=context):
                city = obj.city_id.code
                township = obj.township_id.code
                branch_id = obj.branch_id.branch_code
                nextNumber = obj.nextnumber
                padding = obj.padding
                code = None
                if city and township and branch_id and nextNumber and padding:
                    code =branch_id +'-' + city + '-' + township
                    result = None
                    while(len(str(nextNumber)) <= padding - 1):
                        nextNumber = '0' + str(nextNumber)
                        result = nextNumber
                    if len(str(nextNumber)) > padding - 1:
                        result = str(nextNumber)
                    code = code + '-' + result
                    updateNumber = obj.nextnumber + 1
                    self.write(cr, uid, ids, {'nextnumber':updateNumber}, context=context)
        return code
        
    
res_code()
