# repositories.py
import json
import pathlib
from abc import ABC, abstractmethod
from flask import session
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class AbstractUsersRepo(ABC):
    @abstractmethod
    def all(self, term: str = ""):
        pass

    @abstractmethod
    def get(self, user_id: str):
        pass

    @abstractmethod
    def add(self, user: dict):
        pass

    @abstractmethod
    def update(self, user_id: str, data: dict):
        pass

    @abstractmethod
    def delete(self, user_id: str):
        pass


class FileUsersRepo(AbstractUsersRepo):
    FILE = pathlib.Path("users.json")

    def _load(self):
        try:
            return json.loads(self.FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self, users):
        self.FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")

    def all(self, term=""):
        users = self._load()
        return [u for u in users if term.lower() in u["name"].lower()] if term else users

    def get(self, user_id):
        return next((u for u in self._load() if u["id"] == user_id), None)

    def add(self, user):
        users = self._load()
        users.append(user)
        self._save(users)

    def update(self, user_id, data):
        users = self._load()
        for u in users:
            if u["id"] == user_id:
                u.update(data)
                break
        self._save(users)

    def delete(self, user_id):
        users = [u for u in self._load() if u["id"] != user_id]
        self._save(users)


class SessionUsersRepo(AbstractUsersRepo):
    KEY = "users"

    def _load(self):
        return session.get(self.KEY, [])

    def _save(self, users):
        session[self.KEY] = users

    def all(self, term=""):
        users = self._load()
        return [u for u in users if term.lower() in u["name"].lower()] if term else users

    def get(self, user_id):
        return next((u for u in self._load() if u["id"] == user_id), None)

    def add(self, user):
        users = self._load()
        users.append(user)
        self._save(users)

    def update(self, user_id, data):
        users = self._load()
        for u in users:
            if u["id"] == user_id:
                u.update(data)
                break
        self._save(users)

    def delete(self, user_id):
        users = [u for u in self._load() if u["id"] != user_id]
        self._save(users)


class PostgresUsersRepo(AbstractUsersRepo):
    def __init__(self):
        url = os.getenv("DATABASE_URL")

        if url:
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            self.conn = psycopg2.connect(url)
        else:
            self.conn = psycopg2.connect(
                dbname="flask_users",
                user="olgaakukina",
                password="",
                host="localhost",
                port="5432"
            )


    def all(self, term=""):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            if term:
                cur.execute("SELECT * FROM users WHERE name ILIKE %s", (f"%{term}%",))
            else:
                cur.execute("SELECT * FROM users")
            return cur.fetchall()

    def get(self, user_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return row if row else None

    def add(self, user):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)",
                (user["id"], user["name"], user["email"])
            )
            self.conn.commit()

    def update(self, user_id, data):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET name = %s, email = %s WHERE id = %s",
                (data["name"], data["email"], user_id)
            )
            self.conn.commit()

    def delete(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.conn.commit()
