##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class branch_requisition_wizard(osv.osv_memory):
    _name = "branch.requisition.wizard"  
    
    def recalculate(self, cr, uid, ids, context=None):
               
        if context.get('branch_requisition_id'):
            requisition_id = context.get('branch_requisition_id')
            requisition = self.pool.get('branch.stock.requisition').browse(cr, uid, requisition_id, context=context)  
            if requisition:          
                for line in requisition.p_line:                      
                    result = line.recommend_quantity * requisition.cbm_ratio
                    line.recommend_quantity = result 
                requisition.proceed_existing = True
                        
    def proceed_existing(self, cr, uid, ids, context=None):
        
        if context.get('branch_requisition_id'):
            requisition_id = context.get('branch_requisition_id')
            requisition = self.pool.get('branch.stock.requisition').browse(cr, uid, requisition_id, context=context)  
            if requisition:  
                requisition.proceed_existing = True
                self.pool.get('branch.stock.requisition').confirm(cr, uid, [requisition_id], context=None)
