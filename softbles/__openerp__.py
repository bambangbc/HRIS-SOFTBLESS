{
    'name': 'HR softbles',
    'version': '8.0',
    'author': 'Bambang bagus candra',
    'category': 'Human Resources',
    'sequence': 21,
    'website': 'https://www.odoo.com',
    'summary': 'contract, payroll',
    'description': """
Human Resources Management
==========================

This application enables you to manage important aspects of your company's staff and other details such as their skills, contacts, working time...


You can manage:
---------------
* Employees and hierarchies : You can define your employee with User and display hierarchies
* HR Departments
* HR Jobs
    """,
    'author': 'bambang bagus candra',
    'website': 'https://www.odoo.com/page/employees',
    'depends': ['hr_payroll','hr_attendance','hr_payroll','hr'],
    'data': [
        'contract.xml',
        'master_pajak.xml',
        'working_days.xml',
        'salary_structure.xml',
        'report.xml',
        'attendance.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [ 'static/src/xml/suggestions.xml' ],
}