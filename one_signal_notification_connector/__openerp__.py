{
    'name': 'One Signal Notification Connector',
    'version': '10.0.1.1',
    'category': 'Push Notification',
    'summary': """OneSignal connector helpful in sending push notification service for website(Desktop/Browser) & 
                mobile(Android & iOS) applications. These messages get delivered in real-time and appear in the 
                notification slider.""",
    'author': "Khudrath Ali Baig",
    'maintainer': "Khudrath Ali Baig<alibaigkhudrath@gmail.com>",
    'images': [
        'static/description/screen_shots.gif',
    ],
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [        
        'views/one_signal_notification_view.xml',
        'views/res_users_view.xml',
        'views/one_signal_notification_messages.xml',
        'views/one_signal_users.xml',
        'views/menu.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install':False,
}
