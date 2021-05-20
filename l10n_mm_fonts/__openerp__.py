# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Pyidaungsu TrueType fonts",
    "version" : "1.0",
    "author" : "7th Computing",
    "website" : "http://www.7thcomputing.com",
    "description": """
* This module replaces the standard PDF Type1 fonts with TrueType fonts that have unicode characters for simplified Chinese.
* The module contains the ZawgyiOne.ttf font.
* With this module you can continue to use the old font names in the templates, they will be replaced with the DroidSansFallback.ttf font names every time before creating a pdf.
* If you wish to use your own fonts, you have to place them in addons/l10_mm_fonts directory and replace the font name in the file __init__.py accordingly.
* This Module is based on the original work from GÃ¡bor Dukai module (base_report_unicode)
    """,
    "depends" : ["base", ],
    "category" : "Localization",
    "demo_xml" : [],
    "update_xml" : [],
    "license": "AGPL-3",
    "active": False,
    "installable": True
}
