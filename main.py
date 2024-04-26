from flask import Flask, url_for, render_template, redirect, request
from data import db_session
from forms.user import RegisterForm
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user
from forms.user_login import LoginForm
from data.places import Place
from data.comments import Comment
from forms.comment import CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init("db/hotels.db")
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['POST', 'GET'])
def priv():
    if request.method == 'POST':
        return redirect(f"/{request.form['city']}")
    return render_template('slides.html', link1=f'static/img/Metropol_Facade.jpg',
                           link2=f"{url_for('static', filename='img/koprino.jpg')}",
                           link3=f"{url_for('static', filename='img/mriya-rezort.jpg')}",
                           link4=f"{url_for('static', filename='img/hotel-astoria-facade.jpg')}",
                           link5=f"{url_for('static', filename='img/aktra.jpg')}")


@app.route('/<required_city>')
def find_hotels(required_city):
    db_session.global_init("db/hotels.db")
    db_sess = db_session.create_session()
    hotels = []
    for place in db_sess.query(Place).filter(Place.city == required_city):
        hotel = {}
        hotel['id'] = str(place.id)
        hotel['name'] = place.name
        hotel['address'] = place.address
        hotel['url'] = place.url
        hotel['phones'] = place.phones
        hotel['image'] = place.image
        hotels.append(hotel)
    db_sess.commit()
    return render_template('city_hotels.html', hotels=hotels, required_city=required_city)


@app.route('/check_comments/<place_id>')
def check_comments(place_id):
    db_session.global_init("db/hotels.db")
    db_sess = db_session.create_session()
    reviews = []
    cnt = 0
    for comment in db_sess.query(Comment).filter(Comment.place_id == place_id):
        cnt += 1
        review = {}
        review['content'] = comment.content
        for user in db_sess.query(User).filter(User.id == comment.user_id):
            review['user_name'] = user.name
        reviews.append(review)
    if cnt == 0:
        reviews.append(cnt)
    db_sess.commit()
    return render_template('hotel_comments.html', reviews=reviews, place_id=place_id)


@app.route('/write_comment/<user_id>/<place_id>', methods=['GET', 'POST'])
def write_comment(user_id, place_id):
    form = CommentForm()
    if form.validate_on_submit():
        db_session.global_init("db/hotels.db")
        db_sess = db_session.create_session()
        comment = Comment()
        comment.content = form.content.data
        comment.user_id = user_id
        comment.place_id = place_id
        db_sess.add(comment)
        db_sess.commit()
        return redirect('/')
    return render_template('comment.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    db_session.global_init("db/hotels.db")
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1', debug=True)
