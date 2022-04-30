import fnmatch
import os

from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

import data_handler
import db_data_handler

UPLOAD_FOLDER = './sample_data/images'
ALLOWED_EXTENSIONS = {'jpg', 'png'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(12).hex()


@app.route("/")
@app.route("/list")
def list_questions():
    order_by = request.args.get('order_by', 'id')
    order_direction = request.args.get('order_direction', 'desc')
    db_questions = db_data_handler.get_questions()
    db_questions.sort(key=lambda question: question[order_by], reverse=(order_direction == 'desc'))
    return render_template("list.html", questions=db_questions, order_by=order_by, order_direction=order_direction)


@app.route('/question/<id>', methods=['GET'])
def display_question(id):
    question = db_data_handler.get_question(id)
    db_data_handler.increase_question_view_count(question['id'])
    answers = db_data_handler.get_answer_for_question(id)
    if request.method == 'GET':
        return render_template('question.html', question=question, answers=answers)
    return question, answers


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "GET":
        return render_template("add-question.html")
    if request.method == 'POST':
        image = upload_image()
        new_question = db_data_handler.save_new_question_data({
            'title': request.form.get('title', default="not provided"),
            'message': request.form.get('message', default="not provided"),
            'image': image})
        return redirect('/question/' + str(new_question['id']))


def is_valid(file):
    return 'file' not in request.files or file.filename != "" or allowed_file(file.filename)


@app.route("/question/<id>/delete")
def delete_question(id):
    image_delete_from_server(db_data_handler.get_question(id))
    answers = db_data_handler.get_answer_for_question(id)
    if answers:
        for answer in answers:
            image_delete_from_server(answer)
            db_data_handler.delete_answer(answer.get('id'))
    db_data_handler.delete_question(id)
    return redirect("/")


@app.route("/question/<id>/edit", methods=['GET', 'POST'])
def edit_question(id):
    question = db_data_handler.get_question(id)
    if request.method == 'GET':
        return render_template('edit-question.html', question=question)
    elif request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = save_image(file)
            filepath = url_for('uploaded_file', filename=filename)
            question['image'] = filepath
        db_data_handler.edit_question({'id': id,
                                       'title': request.form.get('title'),
                                       'message': request.form.get('message'),
                                       'image': question['image']})
        return redirect('/question/' + id)


# ------------------- ANSWERS ---------------------- #
@app.route('/question/<id>/new-answer', methods=['GET', 'POST'])
def add_answer(id):
    if request.method == 'GET':
        answers = db_data_handler.get_answer_for_question(id)
        question = db_data_handler.get_question(id)
        question['id'] = str(question.get('id'))
        return render_template('add-answer.html', question=question, answers=answers)
    elif request.method == 'POST':
        db_data_handler.save_answer_data({'message': request.form.get('message'), 'question_id': id,
                                          'image': upload_image()})
        return redirect('/question/' + id)


@app.route('/answer/<id>/delete')
def delete_answer(id):
    question_id = request.args.get('question_id')
    answer_list = db_data_handler.get_answers()
    for answer in answer_list:
        if answer['id'] == str(id):
            image_delete_from_server(answer)
    db_data_handler.delete_answer(id)
    return redirect('/question/' + question_id)


# ------------------- COMMENTS ---------------------- #
@app.route('/question/<id>/new-comment', methods=['GET', 'POST'])
def add_comment(id):
    if request.method == 'GET':
        comments = db_data_handler.get_comment_for_question(id)
        return render_template('new-comment.html', question=db_data_handler.get_question(id), comments=comments)
    elif request.method == 'POST':
        file = request.files['file']
        if file.filename != "" and not allowed_file(file.filename):
            error = display_error_message(id)
            return render_template('error.html', error=error, is_comment=True)
        comment_data = {'message': request.form.get('message'), 'answer_id': id,
                        'image': upload_image()}
        data_handler.save_new_comment(comment_data)
        return redirect('question' + id)


# ------------------- VOTES ---------------------- #
@app.route('/question/<question_id>/vote-up')
def increase_question_vote(question_id):
    db_data_handler.increase_question_vote(question_id)
    return redirect('/list')


@app.route('/question/<question_id>/vote-down')
def decrease_question_vote(question_id):
    db_data_handler.decrease_question_vote(question_id)
    return redirect('/list')


@app.route('/answer/<answer_id>/vote-up')
def increase_answer_vote(answer_id):
    answer = db_data_handler.increase_answer_vote(answer_id)
    return redirect('/question/' + str(answer['question_id']))


@app.route('/answer/<answer_id>/vote-down')
def decrease_answer_vote(answer_id):
    answer = db_data_handler.decrease_answer_vote(answer_id)
    return redirect('/question/' + str(answer['question_id']))


# ------------------- IMAGE ---------------------- #
def image_delete_from_server(item):
    if item['image'] != '':
        url_path = item['image']
        if url_path is not None:
            filename = url_path[len('/uploads/'):]
            filepath = UPLOAD_FOLDER + "/" + filename
            if os.path.exists(filepath):
                os.remove(filepath)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    count = len(fnmatch.filter(os.listdir('./sample_data/images'), '*.*'))
    new_name = "Ask-Mate-" + str(count) + os.urandom(4).hex() + "." + file_extension
    filename = secure_filename(new_name)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return 'NULL'
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return ''
        if file and allowed_file(file.filename):
            filename = save_image(file)
            return url_for('uploaded_file', filename=filename)


@app.route('/question/<id>/delete-image', methods=["GET"])
def edit_delete_image(id):
    question = db_data_handler.get_question(id)
    image_delete_from_server(question)
    question['image'] = ''
    db_data_handler.edit_question(question)
    return redirect('/question/' + id + '/edit')


@app.route("/error")
def display_error_message(id):
    error_dict = {'id': id, "title": "Wrong file type!", "message": "Only .jpg and .png files accepted!"}
    return error_dict


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
