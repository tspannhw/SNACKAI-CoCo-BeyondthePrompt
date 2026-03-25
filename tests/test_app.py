"""
NEXUS-7 // Unit Tests
Tests for Beyond the Prompt Enterprise AI Demo
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── File integrity tests ──────────────────────────────────────────────────

class TestAppFiles:
    """Test that all required files exist and are valid."""

    def test_app_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "app.py"))

    def test_app_no_null_bytes(self, project_dir):
        with open(os.path.join(project_dir, "app.py"), "rb") as f:
            assert b"\x00" not in f.read(), "app.py contains null bytes"

    def test_app_syntax(self, project_dir):
        import py_compile
        py_compile.compile(
            os.path.join(project_dir, "app.py"), doraise=True
        )

    def test_manage_script_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "manage.sh"))

    def test_manage_script_executable(self, project_dir):
        assert os.access(os.path.join(project_dir, "manage.sh"), os.X_OK)

    def test_pyproject_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "pyproject.toml"))

    def test_build_pptx_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "build_pptx.py"))

    def test_build_pptx_syntax(self, project_dir):
        import py_compile
        py_compile.compile(
            os.path.join(project_dir, "build_pptx.py"), doraise=True
        )

    def test_validate_script_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "validate.py"))

    def test_presentation_md_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "presentation.md"))

    def test_demo_queries_exists(self, project_dir):
        assert os.path.exists(os.path.join(project_dir, "demo_queries.sql"))


# ── Private key tests ─────────────────────────────────────────────────────

class TestPrivateKeyLoading:
    """Test key-pair authentication."""

    def test_key_file_exists(self):
        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        assert os.path.exists(key_path), f"Private key not found at {key_path}"

    def test_key_file_permissions(self):
        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        if os.path.exists(key_path):
            mode = oct(os.stat(key_path).st_mode)[-3:]
            assert mode in ("600", "400"), f"Key permissions too open: {mode}"

    def test_key_loads_correctly(self):
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        if not os.path.exists(key_path):
            pytest.skip("Private key not available")

        with open(key_path, "rb") as f:
            key_data = f.read()

        private_key = serialization.load_pem_private_key(
            key_data, password=None, backend=default_backend()
        )
        assert private_key is not None

        pkb = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        assert len(pkb) > 0


# ── Snowflake connection tests ────────────────────────────────────────────

class TestSnowflakeConnection:
    """Test Snowflake connectivity."""

    def test_connection_valid(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1

    def test_adsb_table_exists(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute("SELECT COUNT(*) FROM DEMO.DEMO.ADSB")
        assert cur.fetchone()[0] >= 0

    def test_financial_table_exists(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM DEMO.DEMO.FINANCIAL LIMIT 1")
            assert cur.fetchone()[0] >= 0
        except Exception:
            pytest.skip("FINANCIAL table/view not accessible")


# ── Cortex AI function tests ─────────────────────────────────────────────

class TestCortexAIFunctions:
    """Test Cortex AI functions."""

    def test_ai_sentiment(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute("SELECT AI_SENTIMENT('This is great!')")
        assert cur.fetchone()[0] is not None

    def test_ai_classify(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute(
            "SELECT AI_CLASSIFY('Emergency landing', ['normal','emergency','routine'])"
        )
        assert cur.fetchone()[0] is not None

    def test_ai_complete(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute("SELECT AI_COMPLETE('claude-3-5-sonnet', 'Say hello')")
        result = cur.fetchone()
        assert result[0] is not None
        assert len(result[0]) > 0


# ── Semantic view tests ───────────────────────────────────────────────────

class TestSemanticView:
    """Test semantic view functionality."""

    def test_semantic_view_query(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute(
            "SELECT sv.total_aircraft FROM SEMANTIC_VIEW(DEMO.DEMO.adsb_flight_tracking METRICS total_aircraft) AS sv"
        )
        result = cur.fetchone()
        assert result[0] is not None
        assert result[0] >= 0

    def test_semantic_view_multiple_metrics(self, snowflake_connection):
        cur = snowflake_connection.cursor()
        cur.execute(
            """SELECT sv.total_aircraft, sv.total_flights, sv.avg_altitude, sv.avg_ground_speed
               FROM SEMANTIC_VIEW(DEMO.DEMO.adsb_flight_tracking
                   METRICS total_aircraft, total_flights, avg_altitude, avg_ground_speed) AS sv"""
        )
        row = cur.fetchone()
        assert all(v is not None for v in row), "All metrics should return values"


# ── PowerPoint builder tests ──────────────────────────────────────────────

class TestPowerPointBuilder:
    """Test the PPTX generation script."""

    def test_pptx_module_importable(self):
        import pptx
        assert pptx is not None

    def test_build_pptx_importable(self, project_dir):
        sys.path.insert(0, project_dir)
        try:
            import build_pptx
            assert hasattr(build_pptx, "build_presentation")
        finally:
            sys.path.pop(0)

    def test_build_pptx_generates_file(self, project_dir, tmp_path):
        sys.path.insert(0, project_dir)
        try:
            import build_pptx
            out = str(tmp_path / "test_output.pptx")
            build_pptx.build_presentation(out)
            assert os.path.exists(out)
            assert os.path.getsize(out) > 10000  # should be >10KB
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
