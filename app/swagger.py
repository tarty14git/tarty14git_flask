from flasgger import Swagger

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "com.cth Enterprise Reporting API",
        "description": "API documentation for CTH Enterprise Flask Web Application with Oracle/Postgres/SQL Server dynamic reporting and workflow automation.",
        "contact": {
            "name": "CTH Engineering Team",
            "email": "support@cth.com"
        },
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

def init_swagger(app):
    return Swagger(app, template=swagger_template, config=swagger_config)
