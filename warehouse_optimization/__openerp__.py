# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Warehouse Opitimization',
    'version': '1.0',
    'category': 'Warehouse',
    'sequence': 25,
    'summary': 'Warehouse Opitimization',
    'description': """
Warehouse Opitimization

""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base',      
         'stock','stock_quant_packages_moving_wizard'
 
    ],
    'data': [
        
       #'wizard/quant_packages_stickering_move_wizard_view.xml',
       #'wizard/quant_packages_repacking_move_wizard_view.xml',     
       'views/product_product_view.xml',
       'views/stock_quant_package_view.xml',
        'views/stock_quant_package_transfer_view.xml',
        'views/stock_quant_package_saleable_transfer_view.xml',
       #'views/stock_quant_package_repacking_transfer_view.xml',
       
       
    ],
    #'demo': ['hr_recruitment_demo.xml'],
    #'test': ['test/recruitment_process.yml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
