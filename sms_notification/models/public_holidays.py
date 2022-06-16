from openerp.osv import fields, osv

class public_holidays(osv.osv):
    _name = "public.holidays"
    
    _columns = {
        'name': fields.char(string="Name"),       
        'line_ids': fields.one2many('public.holidays.line', 'holidays_id', 'Holiday Dates'), 
    }
    
class public_holidays_line(osv.osv):

    _name = 'public.holidays.line'
    _description = 'Public Holidays Lines'

    _columns = {        
        'holidays_id': fields.many2one('public.holidays', 'Holiday', ondelete='cascade'),                
        'date': fields.date('Date', required=True),        
    }
    