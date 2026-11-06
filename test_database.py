"""Run with: python test_database.py — tests a temporary database, not the shared one."""
from pathlib import Path
from tempfile import TemporaryDirectory
from database import initialize, add_task, list_tasks, get_task, update_task, set_done, delete_task
with TemporaryDirectory() as d:
    db = Path(d) / 'test.db'
    initialize(db)
    assert list_tasks(db) == []
    t = add_task('CPU4106 Project', 'Computing Mini-Project', '2026-11-09', 'High', db_path=db)
    assert t['title'] == 'CPU4106 Project' and not t['done']
    assert len(list_tasks(db)) == 1
    assert len(list_tasks(db)) == 1  # survives database reconnection
    t = update_task(t['id'], 'CPU4106 edited', 'Computing Mini-Project', '2026-11-11', 'Low', db_path=db)
    assert t['priority']=='Low' and t['date']=='2026-11-11'
    assert set_done(t['id'], True, db) and get_task(t['id'], db)['done']
    assert set_done(t['id'], False, db) and not get_task(t['id'], db)['done']
    assert delete_task(t['id'], db) and list_tasks(db)==[]
    try:
        add_task('', 'Module', '2026-11-11', db_path=db)
        raise AssertionError('blank title incorrectly accepted')
    except ValueError:
        pass
print('PASS — initialise, insert, read, persist, edit, complete, undo, delete, validation')
