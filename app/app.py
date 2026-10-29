"""Assignment submission portal (Flask)."""
import json
import os

from flask import Flask, redirect, render_template, request, url_for

from .validation import validate


def create_app(storage_path=None):
    app = Flask(__name__)
    app.config["STORAGE"] = storage_path or os.environ.get("SUBMISSIONS_FILE", "submissions.json")

    def load():
        try:
            with open(app.config["STORAGE"], encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(items):
        with open(app.config["STORAGE"], "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    @app.get("/")
    def index():
        return render_template("index.html", submissions=load(), errors=[], form={})

    @app.post("/submit")
    def submit():
        form = {k: (request.form.get(k) or "").strip() for k in ("name", "reg_no", "title", "url")}
        errors = validate(form)
        if errors:
            return render_template("index.html", submissions=load(), errors=errors, form=form), 400
        items = load()
        items.append(form)
        save(items)
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
