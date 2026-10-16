CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK(length(username) BETWEEN 3 AND 50),
    name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 1 AND 100),
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Student', 'Faculty', 'Staff', 'Facility Coordinator'))
);
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id),
    category TEXT NOT NULL CHECK(category IN ('Electrical', 'IT & Computer', 'Furniture', 'Plumbing', 'Cleanliness & Sanitation', 'Other')),
    description TEXT NOT NULL CHECK(length(trim(description)) BETWEEN 1 AND 2000),
    building TEXT NOT NULL CHECK(length(trim(building)) BETWEEN 1 AND 100),
    floor TEXT NOT NULL CHECK(length(trim(floor)) BETWEEN 1 AND 100),
    room TEXT NOT NULL CHECK(length(trim(room)) BETWEEN 1 AND 100),
    suggested_priority TEXT CHECK(suggested_priority IN ('Low', 'Medium', 'High')),
    final_priority TEXT CHECK(final_priority IN ('Low', 'Medium', 'High')),
    status TEXT NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'In Progress', 'Resolved', 'Reopened')),
    photo TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    resolution_note TEXT CHECK(resolution_note IS NULL OR length(trim(resolution_note)) BETWEEN 1 AND 2000),
    resolved_by TEXT CHECK(resolved_by IS NULL OR length(trim(resolved_by)) BETWEEN 1 AND 100),
    resolved_at TEXT,
    CHECK(status != 'Resolved' OR (resolution_note IS NOT NULL AND resolved_by IS NOT NULL AND resolved_at IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS issues_reporter_idx ON issues(reporter_id);
CREATE INDEX IF NOT EXISTS issues_status_idx ON issues(status);
