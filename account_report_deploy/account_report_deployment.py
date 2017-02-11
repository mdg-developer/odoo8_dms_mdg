from openerp.osv import fields, osv
import os
import shutil
from openerp.osv import orm
from openerp.tools.translate import _
from xlrd import open_workbook

class account_report_deployment(osv.osv):
    
    _name = 'account.report.deployment'   
       
    _columns = {       
        'to_location': fields.char('Tomcat Path', required=True),
        'report_url': fields.char('Report URL'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('deploy', 'Deployed')         
        ], 'State', readonly=True),
    }
    
    _defaults = {
            'state': 'draft',
    }
    
    def action_deploy_report(self, cr, uid, ids, context=None):
        
        data = self.browse(cr, uid, ids)[0]   
        to_location = data.to_location      
          
        path = os.path.dirname(__file__)       
        fpath = path.replace('\\', '/')
        library_path = fpath + "/library"
        report_path = fpath + "/report"
        script_path = fpath + "/script"
        link_path = fpath + "/report_link"
                
        to_location = to_location.replace('\\', '/')
        report_library_path = to_location 
           
        urlPrefix = data.report_url    
        if os.path.exists(report_library_path):
                       
            for lname in os.listdir(library_path):                      
               
                check_library = report_library_path + "/" + lname
                
                if os.path.isfile(check_library): 
                                   
                    os.remove(check_library)                  
                    shutil.copy(library_path + "/" + lname, report_library_path) 
                   
                else:  
                   
                    shutil.copy(library_path + "/" + lname, report_library_path)                   
            
        else:    
          
            create_folder = to_location + "/birt_report" 
            os.mkdir(create_folder, 0755)
                   
            for lname in os.listdir(library_path):
                  
                shutil.copy(library_path + "/" + lname, report_library_path)           
              
                
        for rname in os.listdir(report_path):
           
            check_report = to_location + "/" + rname
            if os.path.isfile(check_report): 
                             
                os.remove(check_report)                  
              
                shutil.copy(report_path + "/" + rname, to_location)              
            else:  
                   
                shutil.copy(report_path + "/" + rname, to_location)
            
        array = []
        script = ""
        
        for sname in os.listdir(script_path):
                      
             with open(script_path + "/" + sname) as f:
                 for line in f:
                     array.append(line)                     
              
        for i in array:         
            script += i + "\n"
         
        if script:       
            cr.execute(script)
            
        wb = open_workbook(link_path + '/account_report_link.xlsx')
        lines = []
        for s in wb.sheets():            
            headers = []
            header_row = 0            
            for hcol in range(0, s.ncols):               
                headers.append(s.cell(header_row, hcol).value)           
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):                   
                    values.append(s.cell(row, col).value)
                    lines.append(values)       
        if lines:
            for line in lines:
                reportId = None
                reportName = None               
                url = None               
                if len(line) >= 1:
                    reportName = str(line[0])                   
                if len(line) >= 2:
                    url = str(line[1])
                    url = url.split('/', 3)  
                    url = url[3]         
                          
                if url:
                    url = urlPrefix + "/" + url
                if reportName and url:
                    
                    cr.execute(""" select id from account_report where lower(url_name) = %s """, (reportName.lower(),))  # check the report already exist or not
                    data = cr.fetchall()
                    if data:
                        reportId = data[0][0]
                    if reportId:
                        cr.execute(""" update account_report set url_link = %s where id = %s """ , (url, reportId,))
                        
                    else:
                        cr.execute(""" insert into account_report (url_name,url_link) values(%s,%s) """, (reportName, url,))
        self.write(cr, uid, ids, {'state': 'deploy'}, context=context)
        return True   
    
account_report_deployment()   
