# -*- coding: utf-8 -*-

{
    'name': 'Stock Inventory',
    'version': '16.0.1.3',
    'category': 'Generic Modules',
    'summary': """
        Stock Inventory
    """,
    'description': """Stock Inventory""",
    'author': 'KKR',
    'company': 'Evon Technologies Pvt Ltd',
    'maintainer': 'Evon Technologies Pvt Ltd',
    'website': 'https://evontech.com/',
    'depends': ['base',],
    'data': [
        'security/new_sec_groups.xml',
        'security/ir.model.access.csv',
        'views/event.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}