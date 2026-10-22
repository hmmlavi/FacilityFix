"""First-run setup and local production server for FacilityFix."""
import secrets
import sqlite3
import subprocess
import sys
from pathlib import Path

from waitress import serve

ROOT = Path(__file__).resolve().parent
INSTANCE = ROOT / 'instance'
DATABASE = INSTANCE / 'facilityfix.sqlite3'
SECRET_FILE = INSTANCE / 'secret-key'


def main():
    INSTANCE.mkdir(exist_ok=True)
    (ROOT / 'uploads').mkdir(exist_ok=True)
    if not SECRET_FILE.exists():
        SECRET_FILE.write_text(secrets.token_hex(32), encoding='ascii')
    import os
    os.environ['FACILITYFIX_SECRET_KEY'] = SECRET_FILE.read_text(encoding='ascii').strip()

    from app import create_app
    app = create_app()
    with app.app_context():
        from database.connection import init_db
        init_db()
        with sqlite3.connect(DATABASE) as db:
            has_users = db.execute('SELECT EXISTS(SELECT 1 FROM users)').fetchone()[0]

    if not has_users:
        print('\nFirst run: create the Facility Coordinator account. The password is entered privately.')
        result = subprocess.run(
            [sys.executable, '-m', 'flask', '--app', 'app', 'create-user',
             '--role', 'Facility Coordinator'], cwd=ROOT, env=os.environ.copy(), check=False)
        if result.returncode:
            print('Account setup did not finish. Run this launcher again to continue setup.')
            return result.returncode

    print('\nFacilityFix is running at http://127.0.0.1:5000')
    print('Keep this window open while using the application. Press Ctrl+C to stop it.')
    serve(app, host='127.0.0.1', port=5000)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('\nFacilityFix stopped.')
