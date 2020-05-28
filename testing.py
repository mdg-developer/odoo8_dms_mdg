import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.Certificate('D:\\git\\awbab2b_UAT\\tabletsales-1373-firebase-adminsdk-12xpb-9cafccb3de.json')
firebase_admin.initialize_app(cred, {
  'projectId': 'tabletsales-1373',
})

db = firestore.client()
doc_ref = db.collection('users').document('alovelace')
doc_ref.set({
    u'first': u'Ada',
    u'last': u'Lovelace',
    u'born': 1815
})
doc_ref = db.collection('users').document('aturing')
doc_ref.set({
    u'first': u'Alan',
    u'middle': u'Mathison',
    u'last': u'Turing',
    u'born': 1912
})
print (True)