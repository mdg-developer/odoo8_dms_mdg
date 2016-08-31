import ast
data ="{'customer_code':'YGN-MTNT-RT-5385','sale_plan_name':''Saturday','tablet_id':'1','other_reason':'123','visit_reason':'no_shopkeeper','sale_team_id':'18','image':'','sale_plan_day_id':'30','date':'2016-08-17 05:55:09 PM','image2':'','image1':'','sale_team':'18','user_id':'102','longitude':'0.0','latitude':'0.0','image4':'','image3':'','customer_id':'23445','sale_plan_trip_id':''}"

val = ast.literal_eval(data)