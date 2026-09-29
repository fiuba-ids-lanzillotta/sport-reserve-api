import logging
from flask import Flask
from sport_reserve import db
from sport_reserve.constants import BASE_URL
from sport_reserve.routes.deportes import deportes_bp
from sport_reserve.routes.canchas import canchas_bp
from sport_reserve.routes.socios import socios_bp
from sport_reserve.routes.reservas import reservas_bp
from sport_reserve.routes.bloqueos import bloqueos_bp
from sport_reserve.routes.recurrentes import recurrentes_bp

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

def create_app() -> Flask:
    app = Flask(__name__)
    app.json.sort_keys = False
    db.init_app(app)

    app.register_blueprint(deportes_bp,   url_prefix=BASE_URL)
    app.register_blueprint(canchas_bp,    url_prefix=BASE_URL)
    app.register_blueprint(socios_bp,     url_prefix=BASE_URL)
    app.register_blueprint(reservas_bp,   url_prefix=BASE_URL)
    app.register_blueprint(bloqueos_bp,   url_prefix=BASE_URL)
    app.register_blueprint(recurrentes_bp, url_prefix=BASE_URL)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
