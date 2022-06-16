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
{
    'name': 'Tablet Logout Time',
    'version': '1.0',
    'category': 'Tablet Logout Time',
    'sequence': 10,
    'summary': 'Tablet Logout Time',
    
    'description': """
Logout Time Module
=================================================
Welcome to Tablet Logout Time.
    """,
    
    'author': ' 7th Computing Software Development Team',
    'website': 'http://www.7thcomputing.com',
    'images': [],
    
    'depends': [
                'base',
             
                ],
                
                
    'data' : [
              'table_logout_time_view.xml'
    ],
             
    'demo': [],
    'installable': True,
    'auto_install': False,
   
}




