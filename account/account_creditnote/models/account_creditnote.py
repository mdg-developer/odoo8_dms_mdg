from openerp.osv import fields, osv

class account_creditnote(osv.osv):
    _name = 'account.creditnote'
    _columns = {'creditnote_no': fields.char('Credit Note Number'),
                'create_date': fields.date('Create Date'),
                'issued_date': fields.datetime('Issued Date'),
                'used_date': fields.datetime('Used Date'),
                'expired_date': fields.date('Expired Date'),
                'ref_no': fields.char('Approval No'),
                'so_no': fields.char('Source Document'),
                'customer_id':fields.many2one('res.partner', 'Customer', domain="[('customer','=',True)]"),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
                'user_id':fields.many2one('res.users', 'Sale Person'),
                'description': fields.char('Description'),
                'terms_and_conditions': fields.char('Terms and Conditions'),
                'm_status':fields.selection([('new', 'New'), ('issued', 'Issued'),
                                                      ('used', 'Used')], string='Status',default='new'),
                'type':fields.selection({('cash', 'Cash Rebate'), ('stock', 'Stock Rebate')}, string='Type' , required=True),
                'amount': fields.float('Amount'),
                
                }
    
account_creditnote()     