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
    'name': 'MDG SYC TO SD',
    'version': '1.0',
    'category': 'SD',
    'sequence': 30,
    'summary': 'MDG SYC TO SD',
    'description': """
MDG SYC TO SD
""",
    'author': 'Seventh Computing',
    'website': 'http://www.7thcomputing.com',
    'depends': ['base', 'product','sale','sale_promotions','crm_management','sale_journal_principle'],
    'data': [        
             'views/pricelist_view.xml',
             'views/sale_promotion_view.xml',
             'views/res_partner_view.xml',
             'views/sd_connection_view.xml',
             'wizard/price_list_multi_sync_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
