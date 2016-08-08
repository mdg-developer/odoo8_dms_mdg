from datetime import datetime, date, timedelta as td

d1 = datetime.strptime('2008-10-04', '%Y-%m-%d')
d2 = datetime.strptime('2009-10-04', '%Y-%m-%d')

delta = d2 - d1
data = []
for i in range(delta.days + 1):
    str_date = d1 + td(days=i)
    only_month = str_date.strftime('%m')
    only_year = str_date.strftime('%Y')
    month_year = str(only_month + '-' + only_year)
    if month_year not in data:
        data.append(month_year)
print 'months and years are >>> ', data
