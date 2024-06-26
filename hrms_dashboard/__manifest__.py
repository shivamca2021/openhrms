# -*- coding: utf-8 -*-
{
    'name': "Open HRMS - HR Dashboard",
    'version': '16.0.1.61A',
    'summary': """Open HRMS - HR Dashboard""",
    'description': """Open HRMS - HR Dashboard""",
    'category': 'Generic Modules/Human Resources',
    'live_test_url': 'https://youtu.be/XwGGvZbv6sc',
    'author': 'KKR,Open HRMS',
    'company': 'Evon technologies',
    'maintainer': 'Evon technologies',
    'website': "https://www.openhrms.com",
    'depends': ['base','hr', 'hr_holidays', 'hr_timesheet', 'hr_payroll_community', 'hr_contract',
                'hr_attendance', 'hr_timesheet_attendance', 'calendar','stock_inventory',
                'event','spreadsheet_dashboard', 'hr_resignation',
                'hr_reward_warning', 'utm', 'link_tracker'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        'data/new_mail_temp.xml',
        'security/ir.model.access.csv',
        'security/customgroups.xml',
        # 'security/new_sec_groups.xml',
        'report/broadfactor.xml',
        'wizard/monthly_wizard.xml',
        'views/dashboard_views.xml',
        'views/report_field.xml',
        'views/updated_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hrms_dashboard/static/src/css/hrms_dashboard.css',
            'hrms_dashboard/static/src/css/hide_systray.css',
            'hrms_dashboard/static/src/css/lib/nv.d3.css',
            'hrms_dashboard/static/src/js/hrms_dashboard.js',
            # 'hrms_dashboard/static/src/js/hide_systray.js',
            'hrms_dashboard/static/src/js/lib/d3.min.js',
            'hrms_dashboard/static/src/xml/hrms_dashboard.xml',
            'hrms_dashboard/static/src/components/hrms_dashboard/*.js',
            'hrms_dashboard/static/src/components/hrms_dashboard/*.xml',
        ],
    },

    'images': ["static/description/banner.png"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
