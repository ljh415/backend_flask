from flask import Flask, request, jsonify, current_app
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

## Default JSON encoder는 set을 JSON으로 변환 불가능
class CustomJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

def get_user(user_id):
    user = current_app.database.excute(text("""
        SELECT
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id' : user_id
    }).fetchone()  # fetchone은 무엇인가

    return {
        'id' : user['id'],
        'name' : user['name'],
        'email' : user['email'],
        'profile' : user['profile']
    } if user else None

def insert_user(user) :
    return current_app.database.execute(text("""
        INSERT INTO users(
            name,
            email,
            profile,
            hashed_password
        ) VALUE (
            :name,
            :email,
            :profile,
            :password
        )
    """), user).lastrowid

def insert_tweet(user_tweet):
    return current_app.database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        ) VALUES (
            :id,
            :tweet
        )
    """), user_tweet).rowcount

def insert_follow(user_follow):
    return current_app.database.execute(text("""
        INSERT INTO users_follow_list(
            user_id,
            follow_user_id
        ) VALUES (
            :id,
            :foloow
        )
    """), user_follow).rowcount

def insert_unfollow(user_unfollow):
    return current_app.database.execute(text("""
        DELETE FROM users_unfollow
        WHERE user_id = :id
        AND follow_users_id = :unfollow
    """), user_unfollow).rowcount

def get_timeline(user_id):
    timeline = current_app.database.execute(text("""
        SELECT
            t.user_id,
            t.tweet
        FROM tweets t
        LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
        WHERE t.user_id = :user_id
        OR t.user_id = ufl.follow_user_id
    """), {
        'user_id' : user_id
    }).fetchall()

    return [{
        'user_id' : tweet['user_id'],
        'tweet' : tweet['tweet']
    }for tweet in timeline]

def create_app(test_config=None):
    app = Flask(__name__)

    app.json_encoder = CustomJsonEncoder

    if test_config is None :
        app.config.from_pyfile("config.py")
    else :
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow = 0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)

        return jsonify(new_user)

    @app.route('/tweet', methods=['POST'])
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']

        if len(tweet) > 300 :
            return '300자를 초과했습니다', 400

        insert_tweet(user_tweet)

        return '', 200

    @app.route('/follow', methods=['POST'])
    def follow():
        payload = request.json
        insert_follow(payload)

        return '', 200

    @app.route('/unfollow', methods=['POST'])
    def unfollow():
        payload = request.json
        insert_unfollow(payload)

        return '', 200

    @app.route('/timeline/<int:user_id>', methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id' : user_id,
            'timeline' : get_timeline(user_id)
        })

    return app
# def create_app(test_config=None):
#     app = Flask(__name__)
#
#     if test_config is None:
#         app.config.from_pyfile("config.py")
#     else:
#         app.config.update(test_config)
#
#     database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
#     app.database = database
#
#     return app
#
# sign_up() 어차피 안되는 부분
# @app.route("/sign-up", methods=['POST'])
# def sign_up():
#     new_user = request.json
#     new_user_id = app.database.excute(text("""
# 		INSERT INTO users(
# 			name,
# 			email,
# 			profile,
# 			hashed_password
# 		) VALUES (
# 			:name,
# 			:email,
# 			:profile,
# 			:password
# 		)
# 	"""), new_user).lastrowid
#
#     row = current_app.database.excute(text("""
# 		SELECT
# 			id,
# 			name,
# 			email,
# 			profile
# 		FROM users
# 		WHERE id = :user_id
# 	"""), {
#         'user_id': new_user_id
#     }).fetchone()
#
#     created_user = {
#         'id': row['id'],
#         'name': row['name'],
#         'email': row['email'],
#         'profile': row['profile']
#     } if row else None
#
#     return jsonify(created_user)
#
# tweet endpoint
# @app.route('/tweet', methods=['POST'])
# def tweet():
#     user_tweet = request.json
#     tweet = user_tweet['tweet']
#
#     if len(tweet) > 300 :
#         return '300자 초과', 400
#
#     app.database.execute(text("""
#         INSERT INTO tweets(
#             user_id,
#             tweet
#         ) VALUES (
#             :id,
#             :tweet
#         )
#     """), user_tweet)
#
#     return '', 200
#
# timeline 엔드포인트
# @app.route('/timeline/<int:user_id>', methods=['GET'])
# def timeline(user_id):
#     rows = app.database.execute(text("""
#         SELECT
#             t.user_id,
#             t.tweet
#         FROM tweets t
#         LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
#         WHERE t.user_id = :user_id
#         OR  t.user_id = ufl.follow_user_id
#     """), {
#         'user_id' : user_id
#     }).fetchall()
#
#     timeline = [{
#         'user_id' : row['user_id'],
#         'tweet' : row['tweet']
#     } for row in rows]
#
#     return jsonify({
#         'user_id' : user_id,
#         'timeline' : timeline
#     })