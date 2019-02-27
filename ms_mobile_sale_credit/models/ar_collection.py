from openerp.osv import fields, osv

class ar_payment(osv.osv):
    _name = "ar.payment"
    _columns = {               
                   'collection_id':fields.many2one('mobile.ar.collection', 'Line'),
                   'journal_id'  : fields.many2one('account.journal', 'Payment Method' ,domain=[('type','in',('cash','bank'))]),      
                   'amount':fields.float('Paid Amount'),
                   'notes':fields.char('Payment Ref'),
                   'date':fields.date('Date'),
                   'cheque_no':fields.char('Cheque No'),
                   'partner_id':fields.many2one('res.partner', 'Customer'),
                   'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
                   'payment_code':fields.char('Payment Code'),
        }    
    def on_change_journal_id(self, cr, uid, ids, journal_id, ref_no, context=None):
        values = {}
        journal_obj = self.pool.get('account.journal')
        print 'ref_no>>>',ref_no
        if journal_id:
            journal = journal_obj.browse(cr, uid, journal_id, context=context)
            if journal.name =='Cash':
                values = {
                    'payment_code':'CASH',
                    'notes':ref_no,
                    
                }
            elif journal.name =='Bank':
                values = {
                    'payment_code':'BNK',
                    'notes':ref_no,
                }
            elif journal.name =='Cheque':
                values = {
                    'payment_code':'CHEQ',
                    'notes':ref_no,
                }
        return {'value': values}    
class mobile_ar_collection(osv.osv):
    _name = "mobile.ar.collection"
    _description = "AR Collections"
    _columns = {
            #    'name': fields.char('Customer'),
				'partner_id':fields.many2one('res.partner','Customer'),
                'date': fields.date('Payment Date'),
                'so_ref': fields.char('So No'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
				'user_id':fields.many2one("res.users", "Salesman Name"),
                'tablet_id':fields.many2one('tablets.information', 'Tablet Name'),
                'balance': fields.float('Balance'),
                'ref_no': fields.char('Payment Reference'),
                'is_sync':fields.char('Is Sync'),
                'void_flag':fields.char('Void'),
                'customer_code':fields.char('Customer Code'),
                'payment_amount':fields.float('Payment'),
                'so_amount':fields.float('Invoice Amount'),
                'credit_limit':fields.float('Credit Limit'),
                'payment_line_ids':fields.one2many('ar.payment', 'collection_id', 'Payment Lines'),
                'state':fields.selection([('draft', 'Draft'), ('done', 'Done')], 'Status',readonly=True),
                'invoice_id':fields.many2one('account.invoice','Invoice No'),
                'invoice_date':fields.date('Invoice Date'),
                'payment_term':fields.many2one('account.payment.term','Payment Terms'),
                'due_date':fields.date('Due Date'),
                'name':fields.char('Payment Reference',readonly=True),
         'latitude':fields.float('Geo Latitude',  digits=(16, 5), readonly=True),
        'longitude':fields.float('Geo Longitude',  digits=(16, 5), readonly=True),
        'distance_status':fields.char('Distance Status', readonly=True),
    }
    _defaults = {
                 'state' : 'draft',
               
    }
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'ar.collection.code') or '/'
        vals['name'] = id_code
        return super(mobile_ar_collection, self).create(cursor, user, vals, context=context)
    
    def get_ar_collections_datas(self, cr, uid, todayDateNormal, creditPaymentList, saleOrderNoList, context=None, **kwargs):
        ar_collection_obj = self.pool.get('mobile.ar.collection')
        list_val = None
        list_val = ar_collection_obj.search(cr, uid, [('date', '>', todayDateNormal), ('ref_no', 'not in', creditPaymentList), ('so_ref', 'in', saleOrderNoList)])
        print 'list_val', list_val
        list = []
        if list_val:
            for val in list_val:
                cr.execute('select id,name,date,so_ref,sale_team_id,tablet_id,ref_no,is_sync,void_flag,customer_code,payment_amount,so_amount,credit_limit,balance from mobile_ar_collection where id=%s', (val,))
                result = cr.fetchall()
                list.append(result)
                print' list', list
        return list
#         cr.execute('''select id,name,date,so_ref,sale_team_id,tablet_id
#                       balance,ref_no,is_sync,void_flag,customer_code,
#                       payment_amount,so_amount,credit_limit,balance
#                       from mobile_ar_collection where date > %s''', (todayDateNormal,))
#         datas = cr.fetchall()
#         cr.execute
#         return datas
    def on_change_invoice_id(self, cr, uid, ids, invoice_id, context=None):
        values = {}
        invoice_obj = self.pool.get('account.invoice')
        if invoice_id:
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
            values = {
                'ref_no': invoice.number,
                'partner_id': invoice.partner_id.id,
                'invoice_date':invoice.date_invoice,
                'payment_term':invoice.payment_term.id,
                'sale_team_id':invoice.section_id.id,
                'user_id':invoice.user_id.id,
                'branch_id':invoice.branch_id.id,
                'due_date':invoice.date_due,
                'so_amount':invoice.residual,
                'credit_limit':invoice.partner_id.credit_limit,
            }
        return {'value': values}     
    
    def on_change_payment_amount(self, cr, uid, ids, so_amount ,payment_amount, context=None):
        balance=0

        if so_amount and payment_amount:
            balance=so_amount - payment_amount
            
        return {'value': {'balance':balance}}     

    
mobile_ar_collection()


  





     


    
    
    
