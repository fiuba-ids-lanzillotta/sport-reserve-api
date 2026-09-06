"""Configuración compartida de pytest."""
import pytest

import app as app_module


@pytest.fixture
def client():
    """Cliente de prueba de Flask con TESTING activado."""
    app_module.app.config['TESTING'] = True
    return app_module.app.test_client()
