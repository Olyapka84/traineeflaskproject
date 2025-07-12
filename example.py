from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, abort, session
from repositories import FileUsersRepo, SessionUsersRepo, PostgresUsersRepo

import uuid
import json
import psycopg2

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.logger.setLevel("DEBUG")

app.config["USERS_REPO"] = "postgres"

def get_users_repo():
    if app.config["USERS_REPO"] == "session":
        return SessionUsersRepo()
    if app.config["USERS_REPO"] == "postgres":
        return PostgresUsersRepo()
    return FileUsersRepo()


@app.route("/")
def home():
    app.logger.debug("Вызван маршрут / (home)")
    return render_template('home.html')


@app.route('/users/')
def users_index():
    term = request.args.get('term', '')
    app.logger.debug(f"Вызван маршрут /users/ с параметром term='{term}'")
    repo = get_users_repo()
    users = repo.all(term)
    messages = get_flashed_messages(with_categories=True)
    return render_template('users/index.html', users=users, search=term, messages=messages)


@app.route("/courses/<id>")
def courses_show(id):
    return f"Course id: {id}"


@app.route('/users/<id>')
def users_show(id):
    repo = get_users_repo()
    user = repo.get(id)
    if not user:
        abort(404)
    return render_template('users/show.html', user=user)


@app.route("/users/new")
def users_new():
    user = {"name": "", "email": ""}
    errors = {}
    return render_template("users/new.html", user=user, errors=errors)


@app.route("/users", methods=["POST"])
def users_create():
    repo = get_users_repo()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    errors = {}
    if not name:
        errors["name"] = "Имя обязательно"
    if not email:
        errors["email"] = "Email обязателен"
    elif len(name) < 4:
        errors["name"] = "Имя должно быть длинее 4-х символов!"

    if errors:
        user = {"name": name, "email": email}
        return render_template("users/new.html", user=user, errors=errors)

    user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email
    }
    repo.add(user)
    flash("Новый пользователь создан успешно", "success")
    return redirect(url_for("users_index"))


@app.route("/users/<id>/edit")
def users_edit(id):
    repo = get_users_repo()
    user = repo.get(id)
    if not user:
        abort(404)
    return render_template("users/edit.html", user=user, errors={})


@app.route("/users/<id>/patch", methods=["POST"])
def users_patch(id):
    repo = get_users_repo()
    user = repo.get(id)
    if not user:
        abort(404)

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    errors = {}
    if not name:
        errors["name"] = "Имя обязательно"
    if not email:
        errors["email"] = "Email обязателен"
    elif len(name) < 4:
        errors["name"] = "Имя должно быть длинее 4-х символов!"

    if errors:
        user["name"] = name
        user["email"] = email
        return render_template("users/edit.html", user=user, errors=errors)

    repo.update(id, {"name": name, "email": email})
    flash("Данные пользователя обновлены успешно", "success")
    return redirect(url_for("users_index"))


@app.route('/users/<id>/delete', methods=['POST'])
def delete_user(id):
    repo = get_users_repo()
    repo.delete(id)
    flash('Пользователь успешно удален', 'success')
    return redirect(url_for('users_index'))
