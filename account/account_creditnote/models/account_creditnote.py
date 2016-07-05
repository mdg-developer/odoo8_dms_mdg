from openerp.osv import fields, osv

class account_creditnote(osv.osv):
    _name = 'account.creditnote'
    _columns = {
                'name': fields.char('Credit Note Number' ,readonly=True),
                'create_date': fields.date('Create Date'),
                'issued_date': fields.date('Issued Date'),
                'used_date': fields.date('Delivery Date'),
                'ref_no': fields.char('Approval No'),
                'so_no': fields.char('Source Document'),
                'customer_id':fields.many2one('res.partner', 'Customer', domain="[('customer','=',True)]"),
                'sale_team_id':fields.many2one('crm.case.section', 'Sales Team'),
                'user_id':fields.many2one('res.users', 'Salesman Name'),
                'description': fields.char('Description'),
                'terms_and_conditions': fields.char('Terms and Conditions'),
                'm_status':fields.selection([('new', 'New'), ('issued', 'Issued'),
                                                      ('used', 'Used')], string='Status',default='new'),
                'type':fields.selection({('cash', 'Cash Rebate'), ('stock', 'Stock Rebate')}, string='Type' , required=True),
                'amount': fields.float('Amount'),
                
                }
    def create(self, cursor, user, vals, context=None):
        credit_no = self.pool.get('ir.sequence').get(cursor, user,
            'creditnote.code') or '/'
        vals['name'] = credit_no
        return super(account_creditnote, self).create(cursor, user, vals, context=context)    
account_creditnote()     