import connection
from datetime import datetime

NOW = datetime.fromtimestamp(int(datetime.now().timestamp()))


@connection.connection_handler
def get_questions(cursor):  #fetchall()
    query = """
        SELECT id, submission_time, view_number, vote_number, title, message, image
        FROM question
        ORDER BY submission_time"""
    cursor.execute(query)  #wykonaj czytanie po linii
    return cursor.fetchall()


@connection.connection_handler
def get_question(cursor, id):  #fetchone()
    query = f"""
        SELECT *
        FROM question
        WHERE id = {id}
    """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def get_answers(cursor):
    query = f"""
        SELECT *
        from answer
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_answer_for_question(cursor, question_id):
    query = f"""
        SELECT *
        from answer
        WHERE question_id = {question_id}
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_comments(cursor):
    return []


@connection.connection_handler
def get_comment_for_question(cursor, answer_id):
    return []


@connection.connection_handler
def increase_question_view_count(cursor, select_qdict):
    query = f"""
        UPDATE question
        SET view_number = view_number + 1
        WHERE question.id = {select_qdict}
    """
    cursor.execute(query)


@connection.connection_handler
def increase_question_vote(cursor, selected_dictionary):
    query = f"""
        UPDATE question
        SET vote_number = vote_number + 1
        WHERE question.id = {selected_dictionary}
    """
    cursor.execute(query)


@connection.connection_handler
def increase_answer_vote(cursor, selected_dictionary):
    query = f"""
        UPDATE answer
        SET vote_number = vote_number + 1
        WHERE answer.id = {selected_dictionary}
        """
    cursor.execute(query)
    return get_question_id(cursor, selected_dictionary)


@connection.connection_handler
def decrease_question_vote(cursor, selected_dictionary):
    query = f"""
        UPDATE question
        SET vote_number = vote_number - 1
        WHERE question.id = {selected_dictionary}
    """
    cursor.execute(query)
    return get_question_id(cursor, selected_dictionary)


@connection.connection_handler
def decrease_answer_vote(cursor, selected_dictionary):
    query = f"""
        UPDATE answer
        SET vote_number = vote_number - 1
        WHERE answer.id = {selected_dictionary}
            """
    cursor.execute(query)
    return get_question_id(cursor, selected_dictionary)


def get_question_id(cursor, answer_id):
    query = f"""
            SELECT question_id
            from answer
            WHERE id = {answer_id}
            """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def save_new_question_data(cursor, user_input):
    title = user_input['title']
    message = user_input['message']
    image = user_input['image']
    query = f"""
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES('{NOW}', 0, 0, '{title}', '{message}', '{image}')
    """
    cursor.execute(query)
    query = f"""
        SELECT max(id) AS id
        from question
    """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def save_new_comment(cursor, user_input):
    return []


@connection.connection_handler
def edit_question(cursor, updated_dict):
    question_id = updated_dict['id']
    title = updated_dict['title']
    message = updated_dict['message']
    image = updated_dict['image']
    query = f"""
        UPDATE question
        SET title = '{title}', message = '{message}', image = '{image}'
        WHERE question.id = {question_id}
    """
    cursor.execute(query)
    return []


@connection.connection_handler
def save_answer_data(cursor, user_input):
    return []


@connection.connection_handler
def write_over(cursor, file, header, content):
    return []


@connection.connection_handler
def get_new_id(cursor, csvfile):
    return []


@connection.connection_handler
def delete_question(cursor, id):
    return []


@connection.connection_handler
def delete_answer(cursor, id):
    return []
