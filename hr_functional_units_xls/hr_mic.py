from openerp.osv import fields, osv
import openerp

class hr_mic(osv.osv):
    
    _name = 'hr.mic'
   
    _columns = {
       'name':fields.char('Name'),      
    } 
        
hr_mic()