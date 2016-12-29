from openerp.osv import fields, osv

class ar_payment(osv.osv):
    _name = "ar.payment"
    _columns = {               
                   'collection_id':fields.many2one('mobile.ar.collection', 'Line'),
                   'journal_id'  : fields.many2one('account.journal', 'Payment Method' ,domain=[('type','in',('cash','bank'))]),      
                   'amount':fields.float('Paid Amount'),
                   'notes':fields.char('Payment Ref'),
                   'date':fields.date('Date'),
        }    
    
class mobile_ar_collection(osv.osv):
    _name = "mobile.ar.collection"
    _description = "AR Collections"
    _columns = {
                'name': fields.char('Customer'),
				'partner_id':fields.many2one('res.partner','Customer'),
                'date': fields.date('Invoice Date'),
                'so_ref': fields.char('Sale Order No'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
				'user_id':fields.many2one("res.users", "Salesman Name"),
                'tablet_id':fields.many2one('tablets.information', 'Tablet Name'),
                'balance': fields.float('Balance'),
                'ref_no': fields.char('Invoice No'),
                'is_sync':fields.char('Is Sync'),
                'void_flag':fields.char('Void'),
                'customer_code':fields.char('Customer Code'),
                'payment_amount':fields.float('Payment'),
                'so_amount':fields.float('Sale Order Amount'),
                'credit_limit':fields.float('Credit Limit'),
                'payment_line_ids':fields.one2many('ar.payment', 'collection_id', 'Payment Lines'),
                'state':fields.selection([('draft', 'Draft'), ('done', 'Done')], 'Status',readonly=True),
    }
    _defaults = {
                 'state' : 'draft',
               
    }
    
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
     
mobile_ar_collection()


  





     


    
    
    
