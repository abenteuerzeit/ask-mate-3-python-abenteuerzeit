from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape

import data_handler

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def list_questions():
    questions = data_handler.get_questions()
    return render_template("list.html", questions=questions)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("add-question.html")
    elif request.method == "POST":
        data = {'title': request.form['title'], 'message': request.form['message'], 'image': 'None'}
        data_handler.save_question_data(data)
        return render_template("question.html", question=data)
    return redirect('/')


@app.route("/question/<id>/delete")
def delete_question(id):
    if request.method == "GET":
        data_handler.delete_question(id)
    return redirect("/")  # moze tez byc ("/list")


@app.route('/question/<id>')
def display_question(id):
    if request.method == "GET":
        answers = data_handler.get_answer_for_question(id)
        return render_template('question.html', question=data_handler.get_question(id), answers=answers)


# @app.route("/question/<id>/edit")
# def edit_question(id):
#     return render_template('edit-question.html')


@app.route('/question/<id>/new-answer', methods=['GET', 'POST'])
def add_answer(id):
    if request.method == 'GET':
        answers = data_handler.get_answer_for_question(id)
        return render_template('add-answer.html', question=data_handler.get_question(id), answers=answers)
    elif request.method == 'POST':
        answer_data = {'message': request.form['message'], 'question_id': request.form['question_id'], 'image': None}
        data_handler.save_answer_data(answer_data)
        print(id)
        return redirect('/question/' + id)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
