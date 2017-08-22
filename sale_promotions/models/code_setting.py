from openerp.osv import fields, osv

class res_promotion_code(osv.osv):
    _name = "res.promotion.code"
    _columns = {
               'month':fields.char('Month'),
               'year':fields.char( string='Year'),
               'nextnumber':fields.integer(string='Next Number'),
               'padding':fields.integer(string='Padding')
               }
    
    def generateCode(self, cr, uid, ids, context=None):
        code = nextNumber = padding = updateNumber = None
        if ids:
            for obj in self.browse(cr, uid, ids, context=context):
                month = obj.month
                year = obj.year
                nextNumber = obj.nextnumber
                padding = obj.padding
                code = None
                if month and year and nextNumber and padding:
                    code = 'P' +'-' +month+ year 
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
        
    
res_promotion_code()
