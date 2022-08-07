from openerp.osv import fields, osv

class notification_services(osv.TransientModel):
       
    _name = "notification.services"
    _description = "Tablet Notification Services"
    
    def check_promotion(self, cr, uid, sale_team_id , context=None, **kwargs):    
        try:
            cr.execute('''
            select A.id,A.seq,A.from_date,A.to_date,A.p_name from(
            select id,sequence as seq,from_date ,to_date,active,name as p_name, pr.write_date               
                        from promos_rules pr where pr.active = true and main_group in 
                        (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id
                        and pr.active = true
                        and pr.write_date::date = now()::date
                        and cs.id = %s)
                )A where A.write_date::date = now()::date
            ''', (str(sale_team_id),))
            datas = cr.fetchall()            
            return datas
        except Exception, e:            
            return False
    
    def check_tablet_info(self, cr, uid, tablet_id , context=None, **kwargs):    
        try:
            cr.execute('''
                select * from tablets_information where name = %s and write_date::date = now()::date
            ''', (tablet_id,))
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
    
    def update_notification_flag(self, cr, uid, sale_team_id , context=None, **kwargs):    
        try:
            cr.execute('''
                update crm_case_section set is_notification = false where id = %s
            ''', (sale_team_id,))            
        except Exception, e:            
            return False
    
    def  is_any_update(self, cr, uid, sale_team_id, context=None, **kwargs):    
        try:
            print 'Notification Sale Team Id is >>>', sale_team_id
            cr.execute('''select id,code,complete_name from crm_case_section 
                            where write_date::date = now()::date
                            and is_notification = true and id = %s
                            ''', (sale_team_id,))            
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
    
    def  check_sale_team(self, cr, uid, member_id, sale_team_id, context=None, **kwargs):    
        try:
            cr.execute('''
            select DISTINCT cr.id,cr.complete_name,cr.warehouse_id
                    from crm_case_section cr, sale_member_rel sm,crm_case_section_product_product_rel pr 
                    where sm.section_id = cr.id and cr.id=pr.crm_case_section_id  
                    and cr.write_date::date =  now()::date
                    and sm.member_id = %s
                    and cr.id = %s
                            ''', (member_id, sale_team_id,))            
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
    
    def  check_sale_plan_day(self, cr, uid, sale_team_id, context=None, **kwargs):    
        try:
            cr.execute('''
                    select p.id,p.date,p.sale_team
                     from sale_plan_day p
                        join  crm_case_section c on p.sale_team=c.id
                        where p.sale_team= %s
                        and p.write_date::date = now()::date
                        ''', (sale_team_id,))            
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
    
    def check_price_list(self, cr, uid, sale_team_id, context=None, **kwargs):
        try:
            cr.execute('''
                    select A.id,A.name,A.type,A.active,A.write_date from(
                        select id,name,type,active,write_date from product_pricelist 
                        where active = 't' and main_group_id in (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id = %s) or main_group_id is null
                       )A where A.write_date::date = now()::date
                        ''', (sale_team_id,))            
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
        
    def check_product(self, cr, uid, sale_team_id, context=None, **kwargs):    
        try:
            cr.execute('''
                    select  pp.product_tmpl_id,pt.list_price , pt.description
                        from crm_case_section_product_product_rel crm_real ,
                        crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                        where pp.id = crm_real.product_product_id
                        and pt.id = pp.product_tmpl_id
                        and ccs.id = crm_real.crm_case_section_id
                        and pc.id = pt.categ_id
                        and pp.write_date::date = now()::date
                        and ccs.id = %s
                            ''', (sale_team_id,))            
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
    
    def check_sale_plan_trip(self, cr, uid, sale_team_id, context=None, **kwargs):
        try:
            cr.execute('''
                    select p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_trip p
            join  crm_case_section c on p.sale_team=c.id
            where p.sale_team= %s
            and p.write_date::date = now()::date
                ''', (sale_team_id,))            
            datas = cr.fetchall()            
            return datas
        except Exception, e:
            return False
    
    
notification_services()

class tablet_information(osv.osv):
    _inherit = 'tablets.information'
    _columns = {
                'notification_time': fields.char('Schedule Time'),
                }

tablet_information()

class sale_teams(osv.osv):
    _inherit = 'crm.case.section'

    _columns = {                
                'is_notification':fields.boolean('Is_Notification'),                            
                }
    _defaults = {
                'is_notification' : False,
                'status': 0,
    }    
sale_teams()