"""
NEXUS-7 // Shared test fixtures
"""

import os
import pytest


@pytest.fixture(scope="session")
def snowflake_connection():
    """Shared Snowflake connection for the entire test session."""
    import snowflake.connector
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
    if not os.path.exists(key_path):
        pytest.skip("Private key not available")

    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )

    pkb = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    conn = snowflake.connector.connect(
        account="SFSENORTHAMERICA-TSPANN-AWS1",
        user="kafkaguy",
        private_key=pkb,
        role="ACCOUNTADMIN",
        warehouse="INGEST",
        database="DEMO",
        schema="DEMO",
    )
    yield conn
    conn.close()


@pytest.fixture
def project_dir():
    """Return project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
