# A = [1,1,2,3]
# B = [4,5,6,7]
# C = A + B
# print 'C>>',C

# A = [6, 7, 8, 9, 10, 11, 12]
# subset_of_A = set([6, 9, 12]) # the subset of A
# 
# result = [a for a in A if a not in subset_of_A]
# print 'result>>>',result
# 
# list = [["A"], ["A"], ["C"], ["D"], ["C"]]
# 
# values = set(map(lambda x:x[0], list))
# print 'values>>>',values
# newlist = [[y[0] for y in list if y[0]==x] for x in values]
# 
# print 'newlist>>>',newlist

list_one = [{'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'[12106349] NCM-450g', 'ref': False, 'main_group': 633, 'currency_id': False, 'credit': False, 'product_id': 28, 'date_maturity': False, 'debit': 2320.0, 'date': '2016-10-08', 'amount_currency': 0, 'product_uom_id': 26, 'quantity': 1.0, 'partner_id': 33153, 'account_id': 820}, {'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'[AS-C-325ml] AirSoda Can', 'ref': False, 'main_group': 646, 'currency_id': False, 'credit': False, 'product_id': 62, 'date_maturity': False, 'debit': 2375.0, 'date': '2016-10-08', 'amount_currency': 0, 'product_uom_id': 53, 'quantity': 1.0, 'partner_id': 33153, 'account_id': 872}, {'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'[12162761] N 3in1-ESP', 'ref': False, 'main_group': 633, 'currency_id': False, 'credit': False, 'product_id': 20, 'date_maturity': False, 'debit': 3100.0, 'date': '2016-10-08', 'amount_currency': 0, 'product_uom_id': 26, 'quantity': 1.0, 'partner_id': 33153, 'account_id': 820}, None]
#[{'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'[12106349] NCM-450g', 'ref': False, 'main_group': 633, 'currency_id': False, 'credit': 2320.0, 'product_id': 28, 'date_maturity': False, 'debit': False, 'date': '2016-10-08', 'amount_currency': 0, 'product_uom_id': 26, 'quantity': 1.0, 'partner_id': 33153, 'account_id': 820}, {'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'[12162761] N 3in1-ESP', 'ref': False, 'main_group': 633, 'currency_id': False, 'credit': 3100.0, 'product_id': 20, 'date_maturity': False, 'debit': False, 'date': '2016-10-08', 'amount_currency': 0, 'product_uom_id': 26, 'quantity': 1.0, 'partner_id': 33153, 'account_id': 820}, {'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [], 'tax_amount': False, 'name': u'[AS-C-325ml] AirSoda Can', 'ref': False, 'main_group': 646, 'currency_id': False, 'credit': 2375.0, 'product_id': 62, 'date_maturity': False, 'debit': False, 'date': '2016-10-08', 'amount_currency': 0, 'product_uom_id': 53, 'quantity': 1.0, 'partner_id': 33153, 'account_id': 872}]

list_group = [i['main_group'] for i in list_one if i is not None]
print 'i>>>',list_group
val = set(map(lambda x:x, list_group))
print 'val',val
arr_list = []
for v in val:
    print 'v',v
    price = 0
    date_maturity = partner_id = name = date = debit = credit = account_id = analytic_lines = amount_currency = currency_id = tax_code_id = tax_amount = ref = quantity = product_id = product_uom_id = analytic_account_id = None
    result = [a for a in list_one if a is not None and a['main_group'] == v]
    for res in result:
        
        print 'test>>>',res
        price += res['debit']
        date_maturity = res['date_maturity']
        partner_id = res['partner_id']
        name = res['name']
        date = res['date']
        debit = res['debit']
        credit = res['credit']
        account_id = res['main_group'] #replace with product principle AR account
        analytic_lines = res['analytic_lines']
        amount_currency = res['amount_currency']
        currency_id = res['currency_id']
        tax_code_id = res['tax_code_id']
        tax_amount = res['tax_amount']
        ref = res['ref']
        quantity = res['quantity']
        product_id = res['product_id']
        product_uom_id = res['product_uom_id']
        analytic_account_id = res['analytic_account_id']
        print 'res>>>',res['debit']
    print 'price>>',price
    rec = {
                'date_maturity': date_maturity,
                'partner_id': partner_id,
                'name': name,
                'date': date,
                'debit': price,
                'credit': 0,
                'account_id': account_id,
                
                'analytic_lines': analytic_lines,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'tax_code_id': tax_code_id,
                'tax_amount': tax_amount,
                'ref': ref,
                'quantity': quantity,
                'product_id': product_id,
                'product_uom_id': product_uom_id,
                'analytic_account_id': analytic_account_id,
               
            }
    arr_list.append(rec)
print 'arr_list>>>',arr_list             
#     for a in list_one:            
#         
#         if a['main_group'] == v:
#             price += a['credit']       
#         print 'price>>>',price

            