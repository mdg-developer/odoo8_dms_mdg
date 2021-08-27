# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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

from openerp.tools.config import config

import openerp.report
import os

def wrap_trml2pdf(method):
    """We have to wrap the original parseString() to modify the rml data
    before it generates the pdf."""
    def convert2TrueType(*args, **argv):
        """This function replaces the type1 font names with their truetype
        substitutes and puts a font registration section at the beginning
        of the rml file. The rml file is acually a string (data)."""
        odata = args[0]
	fontmap = {
            'Times-Roman':                   'ZawgyiOne',
            'Times-BoldItalic':              'ZawgyiOne',
            'Times-Bold':                    'ZawgyiOne',
            'Times-Italic':                  'ZawgyiOne',

            'Helvetica':                     'ZawgyiOne',
            'Helvetica-BoldItalic':          'ZawgyiOne',
            'Helvetica-Bold':                'ZawgyiOne',
            'Helvetica-Italic':              'ZawgyiOne',
            'Helvetica-Oblique':             'ZawgyiOne',
            'Helvetica-BoldOblique':         'ZawgyiOne',

            'Courier':                       'ZawgyiOne',
            'Courier-Bold':                  'ZawgyiOne',
            'Courier-BoldItalic':            'ZawgyiOne',
            'Courier-Italic':                'ZawgyiOne',
            'Courier-Oblique':               'ZawgyiOne',
            'Courier-BoldOblique':           'ZawgyiOne',

            'Helvetica-ExtraLight':          'ZawgyiOne',

            'TimesCondensed-Roman':          'ZawgyiOne',
            'TimesCondensed-BoldItalic':     'ZawgyiOne',
            'TimesCondensed-Bold':           'ZawgyiOne',
            'TimesCondensed-Italic':         'ZawgyiOne',

            'HelveticaCondensed':            'ZawgyiOne',
            'HelveticaCondensed-BoldItalic': 'ZawgyiOne',
            'HelveticaCondensed-Bold':       'ZawgyiOne',
            'HelveticaCondensed-Italic':     'ZawgyiOne',

            'DejaVu Sans':            'ZawgyiOne',
            'DejaVu Sans BoldItalic': 'ZawgyiOne',
            'DejaVu Sans Bold':       'ZawgyiOne',
            'DejaVu Sans Italic':     'ZawgyiOne',

            'VeraSansYuanTi':          'ZawgyiOne',
        } 
        i = odata.find('<docinit>')
        if i == -1:
            i = odata.find('<document')
            i = odata.find('>', i)
            i += 1
            starttag = '\n<docinit>\n'
            endtag = '</docinit>'
        else:
            i = i + len('<docinit>')
            starttag = ''
            endtag = ''
        data = odata[:i] + starttag
        adp = os.path.abspath(config['addons_path'])
        _localDir=os.path.dirname(__file__)
        _curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
        adp = _curpath
        print adp
        for new in fontmap.itervalues():
            fntp = os.path.normcase(os.path.join(adp, 'fonts', new))
            data += '    <registerFont fontName="' + new + '" fontFile="' + fntp + '.ttf"/>\n'
        data += endtag + odata[i:]
	while len(fontmap)>0:
		ck=max(fontmap)
		data = data.replace(ck,fontmap.pop(ck))
       
        return method(data, args[1:] if len(args) > 2 else args[1], **argv)
    return convert2TrueType

openerp.report.render.rml2pdf.parseString = wrap_trml2pdf(openerp.report.render.rml2pdf.parseString)

openerp.report.render.rml2pdf.parseNode = wrap_trml2pdf(openerp.report.render.rml2pdf.parseNode)
