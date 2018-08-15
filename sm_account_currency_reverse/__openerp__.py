# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Reverse Currency Rate',
    'version': '1.0',
    'depends': ['base','account'],
    'author': 'Siti Mawaddah',
    'description': """
v1.0
----
Make currency conversion rate from other currency not from base currency\n
For example: 1 USD = 12.000 IDR \n
base currency is IDR \n
basic setup is set IDR 1 and set 0.000083333 on USD \n
It will make difficulties to set 1/12.000 on other currency and will affect calculation result \n
By this module. We will just set 1 on IDR and 12.000 on USD and make sure calculation result will be correct

    """,
    'website': 'http://www.berbagiopenerp.blogspot.com',
    'category' : 'Accounting & Finance',
    'depends' : ['base'],
    'data': [
        'views/account_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

