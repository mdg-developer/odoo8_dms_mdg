from openerp.osv import fields, osv

class crypt_password(osv.TransientModel):
    
    _inherit='change.password.user'
    _columns={ 
              'login_password':fields.char('Login Password'),
              }
    def change_password_button(self, cr, uid, ids, context=None):
        print 'Change Password kzo'
        for line in self.browse(cr, uid, ids, context=context):
            line.user_id.write({'password': line.new_passwd})
            line.user_id.write({'login_password': line.new_passwd})   
            user_id=line.user_id.id
            password_id=line.new_passwd
            print 'User ID >>> ', user_id,password_id

            if user_id and password_id: 
#             cr.execute("""select crypt_password(%s,%s)""",(line.user_id,line.new_passwd,))    
                cr.execute("select crypt_password(%s,%s)",(user_id,password_id,))  
               
        # don't keep temporary passwords in the database longer than necessary
        self.write(cr, uid, ids, {'new_passwd': False}, context=context) 
  
crypt_password()

class res_user(osv.osv):
    _inherit='res.users'
    _columns={
              'login_password':fields.char('Login Password')
			  }
 
    def create_extension(self, cr, uid, ids=None, context = None):
        cr.execute("CREATE EXTENSION pgcrypto;");
        return True
    
    def crypt_function(self, cr, uid, ids=None, context=None):
        """Migrate from project.issue.profiling. since this module can completely replace it."""
        if ids is not None:
            raise NotImplementedError("Ids is just there by convention! Please don't use it.")
        
        cr.execute('''
                CREATE OR REPLACE FUNCTION crypt_password(
                p_id integer,
                p_pwd text)
              RETURNS void AS
            $BODY$
            
                #variable_conflict use_variable
                DECLARE l_count int;
                Declare  l_return boolean;
            
            BEGIN
            
                 UPDATE res_users SET login_password =  crypt(p_pwd, gen_salt('md5'))
                 WHERE id = p_id;
            END; 
            
            $BODY$
              LANGUAGE plpgsql VOLATILE
              COST 100;
            ALTER FUNCTION crypt_password(integer, text)
              OWNER TO openerp;
          ''')
        return True
    
res_user()