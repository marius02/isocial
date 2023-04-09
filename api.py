from fastapi import Depends, FastAPI

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get('/')
def hello():
    return 'Hello, World what!'


@app.get('/summary/{video_id}')
async def summary(video_id):
    return summarize(video_id=video_id)


# @app.route('/register', methods=['POST'])
# def register():
#     email = request.form['email']
#     password = request.form['password']

#     cur = conn.cursor()
#     cur.execute("INSERT INTO users (email, password, is_active) VALUES (%s, %s, %s) RETURNING id",
#                 (email, password, False))
#     user_id = cur.fetchone()[0]
#     conn.commit()
#     cur.close()

#     token = generate_confirmation_token(email)
#     confirm_url = f'http://localhost:5000/confirm/{token}'
#     message = Message('Confirm your account', recipients=[email])
#     message.body = f'Thank you for registering. Please confirm your account by clicking the link below:\n\n{confirm_url}'
#     mail.send(message)

#     return jsonify({'message': 'Registration successful. Please check your email for confirmation instructions.'}), 201


# @app.route('/confirm/<token>', methods=['GET'])
# def confirm(token):
#     email = confirm_token(token)
#     if email is None:
#         return jsonify({'message': 'The confirmation link is invalid or has expired.'}), 400

#     cur = conn.cursor()
#     cur.execute("UPDATE users SET is_active = %s WHERE email = %s",
#                 (True, email))
#     conn.commit()
#     cur.close()

#     return jsonify({'message': 'Account confirmed. You can now login.'}), 200


# def generate_confirmation_token(email):
#     s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
#     return s.dumps({'email': email}).decode('utf-8')


# def confirm_token(token, expiration=3600):
#     s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
#     try:
#         data = s.loads(token.encode('utf-8'))
#     except:
#         return None
#     return data.get('email')
