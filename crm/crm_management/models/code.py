padding = 3
nextNumber = 34
result = ''
if nextNumber:
    while(len(str(nextNumber)) <= padding - 1):
        nextNumber = '0' + str(nextNumber)
        result = nextNumber
        print 'nextNumber', nextNumber
    if len(str(nextNumber)) > padding - 1:
        result = str(nextNumber)

print 'next number >>>', result
