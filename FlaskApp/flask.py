from flask import Flask, jsonify, render_template, request
from threading import Thread
from modules import search_db
from chatterbot import ChatBot

app = Flask("", template_folder="FlaskApp/templates/", static_folder="FlaskApp/static/")
app.config["TEMPLATES_AUTO_RELOAD"] = True
chatbot = ChatBot("MikuBot")


@app.route("/")
def main():
    return "Miku still has her coffee."


@app.route("/db")
def db():
    return render_template("main.html")


@app.route("/all")
def all():
    text_list, splitted_text = search_db.search(chatbot.storage, show_numbers=False)
    text_list = [x for x in text_list if x != ""]
    return jsonify({"results": [*set(text_list)]})


@app.route("/search")
def search():
    query = request.args["query"]
    print(f"searching {query}")
    text_list, splitted_text = search_db.search(
        chatbot.storage, query, show_numbers=False
    )
    return jsonify({"results": [*set(text_list)]})


@app.route("/delete")
def delete():
    query = request.args["query"]
    print(request.args["query"])
    print(f"deleting {query}")
    text_list, splitted_text = search_db.search(
        chatbot.storage, query, show_numbers=False
    )
    errors = search_db.delete(chatbot.storage, text_list)
    return str(errors)


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()
