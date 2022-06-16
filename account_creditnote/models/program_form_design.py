from openerp.osv import fields, osv

class program_form_design(osv.osv):
    _name = 'program.form.design'
    _columns = {
                'name': fields.char('Name' ,readonly=False),
                'description': fields.char('Description' ,readonly=False),
                'principle_id':fields.many2one('product.maingroup', 'Principal'),                
                'from_date': fields.date('From Date'),
                'to_date': fields.date('To Date'),
                'term_and_condition': fields.text('Terms and Conditions'),                
                'amount': fields.float('Amount'),
                
                }
    _defaults = {
        'from_date': lambda self,cr,uid,context={}: context.get('from_date', fields.date.context_today(self,cr,uid,context=context)),
        'to_date': lambda self,cr,uid,context={}: context.get('to_date', fields.date.context_today(self,cr,uid,context=context)),
        }  