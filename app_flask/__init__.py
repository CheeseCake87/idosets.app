from flask import Flask, session

from app_flask.extensions import imp, db


def create_app():
    app = Flask(__name__, static_url_path="/")
    imp.init_app(app)
    imp.import_app_resources(
        files_to_import=["routes.py", "error_handlers.py", "cli.py"],
        folders_to_import=[None],
    )
    imp.import_blueprint("api")
    imp.import_models("models")
    db.init_app(app)

    @app.before_request
    def before_request():
        imp.init_session()
        session.permanent = True

    @app.after_request
    def after_request(response):
        if app.config["RUN_ENV"] == "development":
            response.headers.add(
                "Access-Control-Allow-Origin", app.config["VITE_URL"]
            )
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE"
            )
            response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

    return app
