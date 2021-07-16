# -*- coding: utf-8 -*-
{
    'name': "HR Transfer Bank",

    'summary': """
        Create list for bank transfer , list of employees, payroll, and bank account""",

    'description': """
        Export employee payroll as Excel for Bank Transfer
    """,

    'author': "aiksuwandra@gmail.com",
    'website': "http://www.yourcompany.com",

    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll','softbles'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'xport_views.xml',
    ],
    'qweb': [
        'static/src/xml/xport_xcel.xml'
        ],
}
