-- StudyFlow: minimal SQLite schema (two tables; no accounts or online server)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS modules (
    module_id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT NOT NULL UNIQUE CHECK(length(trim(module_name)) > 0)
);

CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY,
    module_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    deadline TEXT NOT NULL CHECK(deadline GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    priority TEXT NOT NULL DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High')),
    done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1)),
    FOREIGN KEY(module_id) REFERENCES modules(module_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_assignments_deadline ON assignments(deadline);
