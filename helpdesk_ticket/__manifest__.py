# -*- coding: utf-8 -*-
{
    'name': "helpdesk_ticket",

    'summary': "Gestion des tickets d’assistance client",

    'description': """
Module de gestion des tickets d'assistance avec workflow, séquence et notifications.
    """,

    'author': "Blackcode",
    'website': "clyde.inov.cm",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Helpdesk',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ticket_sequence.xml',
        'data/ticket_mail_templates.xml',
        'data/ticket_sheduler.xml',
        'reports/ticket_report_templates.xml',
        'reports/ir_action_report.xml',
        'views/ticket_views.xml',
        'views/ticket_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'image': ['static/description/Miniature.gif'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

