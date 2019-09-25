from flask import Flask, request, Response
import lib, db

app = Flask(__name__)

@app.route('/diff/<int:question_id>', methods=['GET'])
@db.with_session
def diff(s, question_id):
    version = request.args.get('version')
    try:
        return Response(
            '\n'.join(lib.gen_diff(s, question_id, version)),
            mimetype = 'text/plain'
        )
    except lib.AppError as e:
        return e.message, 400
    
@app.route('/question/<int:qid>', methods=['PUT'])
@db.with_session
def update_question_text(s, qid):
    # This restriction really should be in middleware, but since this is the only endpoint where the
    # body matters I just chucked it in here. If this check doesn't pass, request.data will be empty
    # and the whole endpoint will blow up.
    if request.content_type != 'text/plain':
        return '', 406

    # I don't fully understand why the body needs to be decoded here. I saw strange behavior where
    # when data was persisted, it somehow "remembered" whether it was str or bytes when it was
    # pulled into memory again. This has to be done because str and bytes don't mix well. Obviously
    # this is something that could easily be checked by mypy.
    text = request.data.decode('utf8')

    try:
        lib.update_question_text(s, qid, text)
        return '', 204
    except AppError as e:
        return e.message, 400
    