# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Aswani PC (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "Open HRMS - HR Dashboard",
    'version': '16.0.1.30',
    'summary': """Open HRMS - HR Dashboard""",
    'description': """Open HRMS - HR Dashboard""",
    'category': 'Generic Modules/Human Resources',
    'live_test_url': 'https://youtu.be/XwGGvZbv6sc',
    'author': 'KKR,Open HRMS',
    'company': 'Evon technologies',
    'maintainer': 'Evon technologies',
    'website': "https://www.openhrms.com",
    'depends': ['base','hr', 'hr_holidays', 'hr_timesheet', 'hr_payroll_community', 'hr_contract',
                'hr_attendance', 'hr_timesheet_attendance', 'calendar', 'project','stock_inventory',
                'hr_recruitment', 'hr_resignation', 'event', 'ohrms_service_request',
                'hr_reward_warning'],
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
