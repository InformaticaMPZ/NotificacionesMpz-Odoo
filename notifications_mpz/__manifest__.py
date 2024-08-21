# -*- coding: utf-8 -*-
{
    "name": "Notifications MPZ",
    "version": "1.0",
    "description": "Notifications MPZ",
    "summary": "Notifications MPZ",
    "author": "Municipalidad de Pérez Zeledón",
    "category": "Administration",
    "depends": ["base", "web"],
    "data": [
        
        "security/res_groups.xml",
        "security/ir_admin_user_access.xml",
        "views/reports/notification_time.xml",

        "views/oracle_email/view_tree.xml",
        "views/oracle_email/view_form.xml",
        "views/oracle_email/actions.xml",
        
        "views/menu.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
