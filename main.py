import json
import pymysql
from custom_exceptions import UserExitException
from menu import (Storage, Question, TestResults, MainMenu, TestMenu, EditMenu)


def fill_storage():
    storage = Storage()
    try:
        with storage.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM question_data")
            q_data = cursor.fetchall()
            cursor.execute("SELECT * FROM question_answers")
            ans_data = cursor.fetchall()
            for q_obj in q_data:
                try:
                    cur_answers = [ans['answer_text'] for ans in ans_data if ans['id'] == q_obj['id']]
                    item = Question(q_obj['id'], q_obj['text'], cur_answers, q_obj['c_answered'], q_obj['w_answered'])
                    storage.questions.append(item)
                except KeyError:
                    pass
    except Exception as ex:
        print(f'Database connection error:', ex)

            
def fill_database():
    storage = Storage()
    try:
        with storage.connection.cursor() as cursor:
            cursor.execute("DELETE FROM question_answers WHERE TRUE")
            cursor.execute("DELETE FROM question_data WHERE TRUE")
            for question in storage.questions:
                query = f"INSERT INTO question_data VALUES ({question.id}, \'{question.text}\', {question.c_answered}, {question.w_answered});"
                cursor.execute(query)
                for ans in question.answers:
                    query1 = f"INSERT INTO question_answers VALUES ({question.id}, \'{ans}\')"
                    cursor.execute(query1) 
            storage.connection.commit()
    except Exception as ex:
        print(f'Database connection error:', ex)


def save_test_results(updated_questions):
    storage = Storage()
    for updated_q in updated_questions:
        for stored_q in storage.questions:
            if stored_q.id == updated_q.id:
                stored_q.c_answered = updated_q.c_answered
                stored_q.w_answered = updated_q.w_answered


def save_edit_results(updated_questions):
    storage = Storage()
    storage.questions = updated_questions


def menu_logic(mode, m_menu, t_menu, e_menu):
    if mode == 'main':
        mode = m_menu.user_id_input()
        return mode
    elif mode == 'test':
        result_list = t_menu.test_logic()
        save_test_results(result_list[0])
        result_menu = TestResults(*result_list)
        mode = result_menu.user_id_input()
        return mode
    elif mode == 'edit':
        save_edit_results(e_menu.edit_logic())
        return 'main'
    elif mode == 'exit':
        raise UserExitException()


def main():
    fill_storage()
    main_menu = MainMenu()
    test_menu = TestMenu()
    edit_menu = EditMenu()
    mode = 'main'
    while True:
        try:
            mode = menu_logic(mode, main_menu, test_menu, edit_menu)
        except UserExitException:
            print('\n\nExiting the programm\nBye bye!')
            fill_database()
            storage = Storage()
            storage.close_db_connection()        
            exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nForced programm shutdown\nBye bye!')
        fill_database()
        storage = Storage()
        storage.close_db_connection()