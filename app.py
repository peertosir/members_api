from flask import Flask, g, request, jsonify
from db import get_db
from functools import wraps



api_username = 'admin'
api_password = "password"

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        else:
            return jsonify({"Error":"Auth failed"}), 403
    return decorated


app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    members_cur = db.execute('select * from members')
    members = members_cur.fetchall()
    result = []
    for member in members:
        result.append({'id':member['id'], 'name':member['name'], 'email':member['email'], 'level':member['level']})
    return jsonify(result)


@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('select * from members where id = ?', [member_id])
    member = member_cur.fetchone()
    return jsonify({'id':member['id'], 'name':member['name'], 'email':member['email'], 'level':member['level']})


@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']
    db = get_db()
    db.execute('insert into members (name, email, level) values (?, ?, ?)', [name, email, level])
    db.commit()

    member_cursor = db.execute('select id, name, email, level from members where name = ?', [name])
    new_member = member_cursor.fetchone()

    return jsonify({'id':new_member['id'], 'name':new_member['name'], 'email':new_member['email'], 'level':new_member['level']})


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    db = get_db()
    member_update = request.get_json()
    name = member_update['name']
    email = member_update['email']
    level = member_update['level']
    db.execute('update members set name = ?, email = ?, level = ?  where id = ?', [name, email, level, member_id])
    db.commit()
    member_cur = db.execute('select * from members where id = ?', [member_id])
    member = member_cur.fetchone()
    return jsonify({'id':member['id'], 'name':member['name'], 'email':member['email'], 'level':member['level']})


@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute('delete from members where id = ? ', [member_id])
    db.commit()
    return jsonify({"message":'Member has been deleted!'})


if __name__ == "__main__":
    app.run()