"""StudyFlow SQLite data access layer. No Flask or third-party packages required.

Maps to the EXISTING JavaScript task shape:
{id: number, title: string, subject: string, date: 'YYYY-MM-DD',
 priority: 'High'|'Medium'|'Low', done: boolean}
"""
from pathlib import Path
from contextlib import closing
import sqlite3
from datetime import date

DB_PATH = Path(__file__).with_name('studyflow.db')
SCHEMA_PATH = Path(__file__).with_name('schema.sql')


def connect(db_path=DB_PATH):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def initialize(db_path=DB_PATH):
    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))


def _validate(title, subject, deadline, priority):
    if not isinstance(title, str) or not title.strip():
        raise ValueError('An assignment title is required')
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError('A subject/module is required')
    if priority not in ('Low', 'Medium', 'High'):
        raise ValueError('Priority must be Low, Medium or High')
    try:
        if date.fromisoformat(deadline).isoformat() != deadline:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError('Deadline must be a valid YYYY-MM-DD date') from None


def _module_id(conn, subject):
    subject = subject.strip()
    conn.execute('INSERT OR IGNORE INTO modules(module_name) VALUES (?)', (subject,))
    return conn.execute('SELECT module_id FROM modules WHERE module_name=?', (subject,)).fetchone()[0]


def add_task(title, subject, date, priority='Medium', done=False, id=None, db_path=DB_PATH):
    """Create a task; optional id lets Flask preserve an existing numeric JS task ID."""
    _validate(title, subject, date, priority)
    if id is not None and (type(id) is not int or id <= 0):
        raise ValueError('id must be a positive integer')
    with closing(connect(db_path)) as conn, conn:
        mid = _module_id(conn, subject)
        if id is None:
            cur = conn.execute('INSERT INTO assignments(module_id,title,deadline,priority,done) VALUES (?,?,?,?,?)',
                               (mid,title.strip(),date,priority,int(bool(done))))
        else:
            cur = conn.execute('INSERT INTO assignments(assignment_id,module_id,title,deadline,priority,done) VALUES (?,?,?,?,?,?)',
                               (id,mid,title.strip(),date,priority,int(bool(done))))
        task_id = cur.lastrowid
    return get_task(task_id, db_path)


def _as_task(row):
    return dict(id=row['assignment_id'], title=row['title'], subject=row['module_name'],
                date=row['deadline'], priority=row['priority'], done=bool(row['done']))


def get_task(id, db_path=DB_PATH):
    with closing(connect(db_path)) as conn, conn:
        row = conn.execute('SELECT a.*,m.module_name FROM assignments a JOIN modules m USING (module_id) WHERE assignment_id=?', (id,)).fetchone()
    return _as_task(row) if row else None


def list_tasks(db_path=DB_PATH):
    with closing(connect(db_path)) as conn, conn:
        rows = conn.execute('SELECT a.*,m.module_name FROM assignments a JOIN modules m USING (module_id) ORDER BY deadline,assignment_id').fetchall()
    return [_as_task(row) for row in rows]


def update_task(id, title, subject, date, priority='Medium', done=False, db_path=DB_PATH):
    _validate(title,subject,date,priority)
    with closing(connect(db_path)) as conn, conn:
        exists = conn.execute('SELECT 1 FROM assignments WHERE assignment_id=?', (id,)).fetchone()
        if not exists: return None
        mid = _module_id(conn, subject)
        conn.execute('UPDATE assignments SET module_id=?,title=?,deadline=?,priority=?,done=? WHERE assignment_id=?',
                     (mid,title.strip(),date,priority,int(bool(done)),id))
    return get_task(id,db_path)


def set_done(id, done=True, db_path=DB_PATH):
    with closing(connect(db_path)) as conn, conn:
        cur=conn.execute('UPDATE assignments SET done=? WHERE assignment_id=?', (int(bool(done)),id))
        return cur.rowcount == 1


def delete_task(id, db_path=DB_PATH):
    with closing(connect(db_path)) as conn, conn:
        cur=conn.execute('DELETE FROM assignments WHERE assignment_id=?',(id,))
        return cur.rowcount == 1
