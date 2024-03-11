# -- coding: utf-8 --
{
    'name': "Open HRMS Service Request",
    'version': '16.0.1.1',
    'summary': """For Requesting Service""",
    'description': """Requesting Services""",
    'category': 'Human Resource',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'oh_employee_creation_from_user', 'project', 'hr_attendance','stock_inventory'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/service_view.xml',
        'views/sequence.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
