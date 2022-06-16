# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2011-2012 Camptocamp SA
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
{'name': 'Customer Feedback',
 'version': '0.1',
 'category': 'SYN',
 'author': "seventh computing",
 'license': 'AGPL-3',
 'website': 'http://www.7thcomputing.com',
 'depends': [
     'base','crm','address_management_system','sale'
 ],
 'init_xml': [],
 'data': [
        'views/customer_feedback_view.xml'
 ],
 'installable': True,
 'active': False,
 }
