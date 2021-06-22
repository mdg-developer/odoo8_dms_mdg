from openerp.tools.config import config
import openerp.tools
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
                'Times-Roman':                   'Pyidaungsu',
                'Times-BoldItalic':              'Pyidaungsu',
                'Times-Bold':                    'Pyidaungsu',
                'Times-Italic':                  'Pyidaungsu',
    
                'Helvetica':                     'Pyidaungsu',
                'Helvetica-BoldItalic':          'Pyidaungsu',
                'Helvetica-Bold':                'Pyidaungsu',
                'Helvetica-Italic':              'Pyidaungsu',
                'Helvetica-Oblique':             'Pyidaungsu',
                'Helvetica-BoldOblique':         'Pyidaungsu',
    
                'Courier':                       'Pyidaungsu',
                'Courier-Bold':                  'Pyidaungsu',
                'Courier-BoldItalic':            'Pyidaungsu',
                'Courier-Italic':                'Pyidaungsu',
                'Courier-Oblique':               'Pyidaungsu',
                'Courier-BoldOblique':           'Pyidaungsu',
    
                'Helvetica-ExtraLight':          'Pyidaungsu',
    
                'TimesCondensed-Roman':          'Pyidaungsu',
                'TimesCondensed-BoldItalic':     'Pyidaungsu',
                'TimesCondensed-Bold':           'Pyidaungsu',
                'TimesCondensed-Italic':         'Pyidaungsu',
    
                'HelveticaCondensed':            'Pyidaungsu',
                'HelveticaCondensed-BoldItalic': 'Pyidaungsu',
                'HelveticaCondensed-Bold':       'Pyidaungsu',
                'HelveticaCondensed-Italic':     'Pyidaungsu',
    
                'DejaVu Sans':            'Pyidaungsu',
                'DejaVu Sans BoldItalic': 'Pyidaungsu',
                'DejaVu Sans Bold':       'Pyidaungsu',
                'DejaVu Sans Italic':     'Pyidaungsu',
    
                'VeraSansYuanTi':          'Pyidaungsu',
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
        for new in fontmap.itervalues():
            fntp = os.path.normcase(os.path.join(adp, 'fonts', new))
            data += '    <registerFont fontName="' + new + '" fontFile="' + fntp + '.ttf"/>\n'
        data += endtag + odata[i:]
        while len(fontmap)>0:
            ck=max(fontmap)
            data = data.replace(ck,fontmap.pop(ck))
           
            return method(data, args[1:] if len(args) > 2 else args[1], **argv)
        odoo.tools.pdf.merge_pdf(method(data, args[1:] if len(args) > 2 else args[1], **argv))
        return convert2TrueType
