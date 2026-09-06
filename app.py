import logging
from flask import Flask
from sport_reserve.constants import BASE_URL
from sport_reserve.routes.deportes import deportes_bp
from sport_reserve.routes.canchas import canchas_bp
from sport_reserve.routes.socios import socios_bp
from sport_reserve.routes.reservas import reservas_bp

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)
app.json.sort_keys = False

app.register_blueprint(deportes_bp, url_prefix=BASE_URL)
app.register_blueprint(canchas_bp,  url_prefix=BASE_URL)
app.register_blueprint(socios_bp,   url_prefix=BASE_URL)
app.register_blueprint(reservas_bp, url_prefix=BASE_URL)

if __name__ == '__main__':
    app.run(debug=True)
