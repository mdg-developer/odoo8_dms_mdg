{
    'name': 'Odoo WooCommerce Connector',
    'version': '8.0',
    'category': 'Sales',
    'license': 'Other proprietary',
    'summary' : 'Integrate & Manage all your WooCommerce operations from Odoo',
    'description': """
This module used to smoothly integrate your WooCommerce Store with Odoo. \n

After installation of our module, you can manager following WooCommerce operations in Odoo, \n
  
Our module supports following features related to WooCommerce. \n

* Multi WooCommerce Stores in single Odoo Instance \n
* WooCommerce Navigation Dashboard \n
* WooCommerce Account Configuration and Setup \n 
* Export Products (With and Without Variations) \n
* Export/Update/Sync Product Gallery images with Product Export/Update/Sync \n
* Export Product Category (Parent Child Category upto any level) \n 
* Update & Sync the Odoo Products, Categories & Tags \n 
* Publish/Unpblish Products in WooCommerce \n 
* Update Product Price,Product Stock to WooCommerce \n
* Auto/Manual Import WooCommerce Orders \n 
* Export Inventory to WooCommerce \n 
* Update Order Status in WooCommerce \n 
* Create Delivery Order, Invoices & Payment Automatically \n 
* Cancel & Refund Order in WooCommerce \n 
* WooCommerce Sales Analysis Report \n 
* Mismatch Logs of Transactions between WooCommerce & Odoo \n
    
====================================================================

For support on this module contact us at info@emiprotechnologies.com \n

To subscribe our support packages visit following link, \n

http://www.emiprotechnologies.com/odoo/support \n 

Visit following link to find our other cool apps to shape your system . \n

https://www.odoo.com/apps/modules?author=Emipro%20Technologies%20Pvt.%20Ltd. \n

For more information about us, visit www.emiprotechnologies.com \n    
""",
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'depends': ['sale_stock','auto_invoice_workflow_ept', 'delivery'],    
    'data': ['security/group.xml',
             'data/import_order_status.xml',
             'views/woo_instance_view.xml',
             'wizard/res_config_view.xml',
             'views/woo_template_view.xml',
             'views/woo_product_image_view.xml',
             'views/woo_variant_view.xml',
             'views/res_partner.xml',
             'views/sale_workflow_config.xml',             
             'views/sale_order.xml',
             'views/stock_picking_view.xml',
             'views/stock_quant_package_view.xml',
             'views/woo_tags_ept.xml',
             'views/woo_product_categ_view.xml',
             'views/account_invoice_view.xml',
             'views/woo_process_job.xml',
             'views/woo_payment_gateway_view.xml',
             'views/woo_coupons_view.xml',
             'wizard/woo_process_import_export_view.xml',
             'wizard/woo_cancel_order_wizard_view.xml',
             'views/operations_view.xml',
             'views/sale_report_view.xml',             
             'security/ir.model.access.csv',
             'data/woo.commerce.operations.ept.csv',
             'views/web_templates.xml',
             'views/ir_cron.xml'                
             ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
    'live_test_url':'http://www.emiprotechnologies.com/free-trial?app=woo-commerce-ept&version=8',    
    'active': False,
    'price': 399.00,
    'currency': 'EUR',
    'images': ['static/description/woocommerce-odoo-cover.jpg'],
}
