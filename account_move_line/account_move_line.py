from openerp.osv import fields, osv

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    _columns = {
                'remark': fields.char('Remark 1'),
                'remark2': fields.char('Remark 2'),
                'remark3': fields.char('Remark 3'),
                'remark4': fields.char('Remark 4'),
                'remark5': fields.char('Remark 5'),
                }