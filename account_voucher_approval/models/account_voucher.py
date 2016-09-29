from openerp.osv import fields, osv

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
                        'state':fields.selection(
                        [('draft', 'Draft'),
                         ('cancel', 'Cancelled'),
                         ('finance_approve', 'Finance Approved'),
                         ('cashier_approve', 'Cashier Approved'),
                         ('proforma', 'Pro-forma'),
                         ('posted', 'Posted')
                        ], 'Status', readonly=True, track_visibility='onchange', copy=False,
                        help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                                    \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                                    \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                                    \n* The \'Cancelled\' status is used when user cancel voucher.'),
              }
    
    def finance_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'finance_approve'}, context=None)
        return True
    
    def cashier_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cashier_approve'}, context=None)
        return True
account_voucher()
