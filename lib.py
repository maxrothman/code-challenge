import difflib
import db

def make_dummy_data(session):
    with db.in_session() as s:
        users = [db.create_user(s, sex, age) for sex, age in [(db.Sex.MALE, 22), (db.Sex.TRANS_FEMALE, 53)]]
        qtexts = [db.create_question(s, q)[1] for q in ["Question 1 v1", "Question 2 v1"]]
        s.flush()
        [db.save_answer(s, q.id, u.id, q.text + " answered v1") for q in qtexts for u in users]
        new_qtexts = [db.update_question_text(s, q.id, q.text[:-1] + "2") for q in qtexts]
        s.flush()
        [db.save_answer(s, q.id, u.id, q.text + " answered v2") for q in new_qtexts for u in users]
        new_new_qtexts = [db.update_question_text(s, q.id, q.text[:-1] + "3") for q in new_qtexts]
        s.flush()
        [db.save_answer(s, q.id, u.id, q.text + " answered v3") for q in new_new_qtexts for u in users]

        
def _diff_question_texts(qtext1, qtext2):
    return difflib.Differ().compare(qtext1.text.split('\n'), qtext2.text.split('\n'))


class AppError(Exception): pass


def gen_diff(s, question_id, version=None):
    if version is None:
        qtext = db.get_latest_question_text(s, question_id)
    else:
        qtext = db.get_question_text_by_version(s, question_id, version)
        
    if qtext is None:
        # This is obviously a bit of a shortcut. It'd be nice to be able to tell which theing
        # doesn't exist.
        raise AppError("Question/Version does not exist")
    
    if qtext.version == 0:
        raise AppError("Version must be >= 1 (there must be a previous version to diff against)")
        
    prev_qtext = db.get_question_text_by_version(s, question_id, qtext.version-1)
    return _diff_question_texts(prev_qtext, qtext)


def update_question_text(s, question_id, text):
    old_qtext = db.get_latest_question_text(s, question_id)
        
    if old_qtext is None:
        raise AppError("Question does not exist")
    
    db.update_question_text(s, old_qtext.id, text)