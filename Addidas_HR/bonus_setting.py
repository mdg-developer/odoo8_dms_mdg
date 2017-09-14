# -*- coding: utf-8 -*-
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


from openerp import tools
from openerp.osv import fields, osv
from openerp import workflow


class hr_bonus(osv.osv):
    _name = 'hr.bonus'
    _description = "Bonus Setting"
     
    _columns = {
               'full_skill_amt':fields.float('Full Skill Amount',required=True),
              'multi_skill_amt':fields.float('Multi Skill Amount',required=True),
              'factory_driver_license_amt':fields.float('Factory Driver License Bonus',required=True),
              'electricity_certificate_amt':fields.float('Electricity Certificate Bonus',required=True),
              'language_line_ids': fields.one2many('hr.language.input', 'language_id', 'Language Inputs'),
              'position_line_ids': fields.one2many('hr.position.input', 'position_id', 'Position Inputs'),
              'critical_line_ids': fields.one2many('hr.critical.input', 'critical_id', 'Critical Inputs'),

             

              }
class hr_position_input(osv.osv):
    '''
    Language Input
    '''

    _name = 'hr.position.input'
    _description = 'Position Input'
    _columns = {
            'position_id':fields.many2one('hr.bonus', 'Position')  ,
            'name':fields.char('Grade', required=True),
            'job_id':fields.many2one('hr.job', 'Job Position'),
            'job_position_amt':fields.float('Amount', required=True) ,
          
        
    }
   
    
class hr_language_input(osv.osv):
    '''
    Language Input
    '''

    _name = 'hr.language.input'
    _description = 'Language Input'
    _columns = {
        'language_id':fields.many2one('hr.bonus', 'Language')  ,
        'name':fields.integer('Grade', required=True),
        'language_capacity':fields.char('Capacity', required=True),
        'language_bonus_amt':fields.float('Bonus Amount', required=True),
        
        
    }

class hr_critical_skill_input(osv.osv):
    '''
    Critical Input
    '''

    _name = 'hr.critical.input'
    _description = 'Critical Input'
    _columns = {
                'critical_id':fields.many2one('hr.bonus','Critical')  ,  
                'name':fields.char('Grade',required=True),
                'critical_skill_amt':fields.float('Amount',required=True) ,    
                'critical_skill_terms':fields.char('Terms',required=True),
                    
                }   
        
     
    
    
