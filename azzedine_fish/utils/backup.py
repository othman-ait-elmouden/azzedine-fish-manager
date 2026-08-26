from datetime import datetime
from pathlib import Path
import shutil, sqlite3
from config import DB_PATH, BACKUP_DIR

def create_backup():
    target=BACKUP_DIR/f"backup_{datetime.now():%Y%m%d_%H%M%S}.db"
    src=sqlite3.connect(str(DB_PATH)); dst=sqlite3.connect(str(target))
    with dst: src.backup(dst)
    src.close(); dst.close(); return target

def restore_backup(source):
    source=Path(source)
    if not source.exists() or source.suffix.lower()!=".db": raise ValueError("ملف النسخة غير صالح")
    test=sqlite3.connect(str(source)); ok=test.execute("PRAGMA integrity_check").fetchone()[0]; test.close()
    if ok!="ok": raise ValueError("قاعدة البيانات تالفة")
    safety=BACKUP_DIR/f"before_restore_{datetime.now():%Y%m%d_%H%M%S}.db"; shutil.copy2(DB_PATH,safety); shutil.copy2(source,DB_PATH)
    return safety

