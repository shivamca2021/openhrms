# -*- coding: utf-8 -*-
{
    'name': 'HRMS',
    'version': '16.0.1.5',
    'summary': 'EvonTech HRMS system',
    'sequence': 10,
    'description': """
    EvonTech HRMS system
""",
    'category': 'Custom',
    # 'website': 'https://www.odoo.com/app/invoicing',
    'images': [],
    'depends': ['base', 'hr', 'contacts', 'hr_attendance', 'project', 'hr_holidays'],
    'data': [
        # 'data/website_data.xml',
        # 'views/assets.xml',
        # 'views/sample_website_templates.xml',
        'security/ir.model.access.csv',
        'security/security_rule.xml',
        'wizard/checkout_wizard_view.xml',
        'views/attendance_record_view.xml',
        'views/custom_user_type.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    # 'post_init_hook': '_account_post_init',
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_common': [
            # 'practice_module/static/src/scss/practice_module.scss',
            # 'practice_module/static/src/scss/practice_module.css'
        ],
        'web.assets_backend': [
            'HRMS/static/src/js/hrms.js',
            # 'practice_module/static/src/scss/practice_module.css'
        ],
        'web.assets_frontend': [
            # '/practice_module/static/src/scss/practice_module.scss',
            # 'practice_module/static/src/scss/practice_module.css'
        ],
    },
    'license': 'LGPL-3',
}
