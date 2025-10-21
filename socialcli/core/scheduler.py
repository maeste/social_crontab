"""Scheduler system for managing scheduled posts.

Implements a SQLite-based queue for scheduling posts across all providers.
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class Scheduler:
    """Manages scheduled posts using SQLite database.

    Database schema:
    - id: Unique post identifier
    - provider: Social platform name (linkedin, x, bluesky, etc.)
    - author: User identifier
    - file_path: Path to post content file
    - publish_at: Scheduled publication timestamp
    - status: Post status (pending, published, failed)
    - created_at: Record creation timestamp
    - updated_at: Last update timestamp
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize scheduler with database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to ~/.socialcli/scheduler.db
        """
        if db_path is None:
            db_path = Path.home() / '.socialcli' / 'scheduler.db'

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    author TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    publish_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def schedule_post(
        self,
        provider: str,
        author: str,
        file_path: str,
        publish_at: datetime
    ) -> int:
        """Schedule a new post.

        Args:
            provider: Social platform name
            author: User identifier
            file_path: Path to post content file
            publish_at: When to publish the post

        Returns:
            Database ID of the scheduled post
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO scheduled_posts (provider, author, file_path, publish_at)
                VALUES (?, ?, ?, ?)
                """,
                (provider, author, file_path, publish_at)
            )
            conn.commit()
            return cursor.lastrowid

    def get_pending_posts(self) -> List[Dict[str, Any]]:
        """Get all pending posts that should be published.

        Returns:
            List of pending posts with publish_at <= now
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM scheduled_posts
                WHERE status = 'pending' AND publish_at <= ?
                ORDER BY publish_at ASC
                """,
                (datetime.now(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_status(self, post_id: int, status: str):
        """Update the status of a scheduled post.

        Args:
            post_id: Database ID of the post
            status: New status (pending, published, failed)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE scheduled_posts
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, post_id)
            )
            conn.commit()

    def list_all(self) -> List[Dict[str, Any]]:
        """List all scheduled posts.

        Returns:
            List of all scheduled posts
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM scheduled_posts ORDER BY publish_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
