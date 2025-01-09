# -*- coding: utf-8 -*-
{
        "name" : "Fabricación Custom",
        "version" : "1.0",
        "author" : "César Rodríguez",
        'license': 'LGPL-3',
        "website" : "https://conetechcr.com",
        "category" : "Reparaciones",
        "summary": """Gestión de Fabricación [Custom]""",
        "description": """Gestión de Fabricación [Custom]""",
        "depends" : ['base','mrp'],
        "data" : [
                  "wizard/change_workcenter.xml",
                  "wizard/dispatch_by_product_views.xml",
                  "security/ir.model.access.csv",
                  "views/product_product_views.xml",
                  "views/mrp_views.xml",
                  ],
        "installable": True
}