#!/usr/bin/env python3
"""
NEXUS-7 // Validation Script
Validates all components of the Beyond the Prompt demo
"""

import sys
import os

CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
RESET = "\033[0m"


def log(status, msg):
    icons = {"OK": f"{GREEN}✓{RESET}", "FAIL": f"{RED}✗{RESET}", "WARN": f"{YELLOW}!{RESET}", "INFO": f"{CYAN}→{RESET}"}
    print(f"  {icons.get(status, '?')} {msg}")


def validate_files():
    print(f"\n{CYAN}[1/6] FILE VALIDATION{RESET}")
    required = ["app.py", "manage.sh", "pyproject.toml", "demo_queries.sql", "presentation.md", "build_pptx.py", "tests/test_app.py"]
    project_dir = os.path.dirname(os.path.abspath(__file__))
    all_ok = True

    for f in required:
        path = os.path.join(project_dir, f)
        if os.path.exists(path):
            log("OK", f"{f}")
        else:
            log("FAIL", f"{f} NOT FOUND")
            all_ok = False

    # Check for null bytes in app.py
    app_path = os.path.join(project_dir, "app.py")
    if os.path.exists(app_path):
        with open(app_path, "rb") as f:
            if b"\x00" in f.read():
                log("FAIL", "app.py contains null bytes")
                all_ok = False
            else:
                log("OK", "app.py clean (no null bytes)")

    return all_ok


def validate_dependencies():
    print(f"\n{CYAN}[2/7] DEPENDENCY VALIDATION{RESET}")
    all_ok = True
    deps = [
        ("streamlit", "Streamlit dashboard"),
        ("snowflake.connector", "Snowflake connector"),
        ("pandas", "Data manipulation"),
        ("plotly", "Charting"),
        ("cryptography", "Key-pair auth"),
        ("pptx", "PowerPoint generation"),
    ]
    for mod, desc in deps:
        try:
            __import__(mod)
            log("OK", f"{mod} ({desc})")
        except ImportError:
            log("FAIL", f"{mod} NOT INSTALLED ({desc})")
            all_ok = False
    return all_ok


def validate_private_key():
    print(f"\n{CYAN}[3/7] PRIVATE KEY VALIDATION{RESET}")
    key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")

    if not os.path.exists(key_path):
        log("FAIL", f"Key not found: {key_path}")
        return False

    log("OK", f"Key exists: {key_path}")

    # Check permissions
    mode = oct(os.stat(key_path).st_mode)[-3:]
    if mode in ("600", "400"):
        log("OK", f"Permissions: {mode}")
    else:
        log("WARN", f"Permissions too open: {mode} (should be 600)")

    # Test loading
    try:
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

        pkb = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        log("OK", f"Key loads correctly ({len(pkb)} bytes)")
        return True
    except Exception as e:
        log("FAIL", f"Key load error: {e}")
        return False


def validate_snowflake_connection():
    print(f"\n{CYAN}[4/7] SNOWFLAKE CONNECTION{RESET}")
    try:
        import snowflake.connector
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

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

        cur = conn.cursor()
        cur.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
        user, role, wh = cur.fetchone()
        log("OK", f"User: {user}")
        log("OK", f"Role: {role}")
        log("OK", f"Warehouse: {wh}")
        conn.close()
        return True
    except Exception as e:
        log("FAIL", f"Connection failed: {e}")
        return False


def validate_data_tables():
    print(f"\n{CYAN}[5/7] DATA TABLES{RESET}")
    try:
        import snowflake.connector
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

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
        cur = conn.cursor()

        # ADSB table
        cur.execute("SELECT COUNT(*) FROM DEMO.DEMO.ADSB")
        count = cur.fetchone()[0]
        log("OK", f"ADSB: {count:,} rows")

        # FINANCIAL table
        try:
            cur.execute("SELECT COUNT(*) FROM DEMO.DEMO.FINANCIAL")
            count = cur.fetchone()[0]
            log("OK", f"FINANCIAL: {count:,} rows")
        except Exception:
            log("WARN", "FINANCIAL table not accessible")

        conn.close()
        return True
    except Exception as e:
        log("FAIL", f"Table check failed: {e}")
        return False


def validate_cortex_functions():
    print(f"\n{CYAN}[6/7] CORTEX AI FUNCTIONS{RESET}")
    try:
        import snowflake.connector
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

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
        cur = conn.cursor()

        # AI_SENTIMENT
        cur.execute("SELECT AI_SENTIMENT('Test message')")
        log("OK", "AI_SENTIMENT")

        # AI_CLASSIFY
        cur.execute("SELECT AI_CLASSIFY('Test', ['a','b']):label::STRING")
        log("OK", "AI_CLASSIFY")

        # AI_COMPLETE
        cur.execute("SELECT AI_COMPLETE('claude-3-5-sonnet', 'Hi')")
        log("OK", "AI_COMPLETE")

        conn.close()
        return True
    except Exception as e:
        log("FAIL", f"Cortex function failed: {e}")
        return False


def validate_semantic_view():
    print(f"\n{CYAN}[7/7] SEMANTIC VIEW{RESET}")
    try:
        import snowflake.connector
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        key_path = os.path.expanduser("~/.snowflake/keys/snowflake_private_key.p8")
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

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
        cur = conn.cursor()

        cur.execute(
            "SELECT sv.total_aircraft FROM SEMANTIC_VIEW(DEMO.DEMO.adsb_flight_tracking METRICS total_aircraft) AS sv"
        )
        result = cur.fetchone()[0]
        log("OK", f"adsb_flight_tracking: {result} aircraft")

        conn.close()
        return True
    except Exception as e:
        log("FAIL", f"Semantic view failed: {e}")
        return False


def main():
    print(f"""
{CYAN}╔═══════════════════════════════════════════════════════════════╗
║  NEXUS-7 VALIDATION SUITE                                      ║
║  Beyond the Prompt // Enterprise AI Demo                       ║
╚═══════════════════════════════════════════════════════════════╝{RESET}
""")

    results = []
    results.append(("Files", validate_files()))
    results.append(("Dependencies", validate_dependencies()))
    results.append(("Private Key", validate_private_key()))
    results.append(("Snowflake Connection", validate_snowflake_connection()))
    results.append(("Data Tables", validate_data_tables()))
    results.append(("Cortex Functions", validate_cortex_functions()))
    results.append(("Semantic View", validate_semantic_view()))

    print(f"\n{CYAN}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{CYAN}SUMMARY{RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{RESET}")

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name}")

    print(f"\n  {passed}/{total} validations passed")

    if passed == total:
        print(f"\n{GREEN}ALL SYSTEMS OPERATIONAL{RESET}\n")
        return 0
    else:
        print(f"\n{RED}VALIDATION FAILURES DETECTED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
