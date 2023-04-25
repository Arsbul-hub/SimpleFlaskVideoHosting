import base64
import io
from datetime import datetime
import os
from tempfile import SpooledTemporaryFile

from PIL import Image
from flask import render_template, send_from_directory, url_for, render_template_string, flash, redirect, request
from flask_ckeditor import upload_fail, upload_success
from werkzeug.datastructures import FileStorage

from app import app, morph, db

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Studios, VideoPosts, Resource
from app.forms import LoginForm, RegistrationForm, AddVideoForm, CreateStudioForm
from werkzeug.urls import url_parse
from app import login

from urllib.parse import unquote


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/files/<path:filename>')
def uploaded_files(filename):
    return send_from_directory("static/loaded_media", filename)


@app.route('/reload_auth')
def reload_auth_system():
    messages = ["Конфигурационный файл аутентификации пользователей был перезагружен!"]
    if not User.query.filter_by(username="Admin").first():
        admin = User(username="Admin")
        admin.set_password("admin")
        db.session.add(admin)

        db.session.commit()
        logout_user()

    return render_template("service/Уведомление.html", user=current_user, title="Внимание", messages=messages)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('top')
        return redirect(next_page)
    return render_template('login.html', is_user_authenticated=current_user.is_authenticated, title='Sign In',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        # login_user(user, remember=form.remember_me.data)
        flash('Congratulations, you are now a registered admin!')
        return redirect("/")
    return render_template('register.html', is_user_authenticated=current_user.is_authenticated, title='Register',
                           form=form)


@app.route('/upload', methods=['POST', "GET"])
def upload():
    f = request.files.get('upload')
    # Add more validations here
    save_file(f)

    url = url_for('uploaded_files', filename=f.filename)

    return upload_success(url, filename=f.filename)


def save_file(file, path="/media", name=None, formates=[]):
    if not file:
        return None
    format = file.filename.split(".")[-1].lower()
    if name:
        file.filename = name + "." + format

    if formates and format not in formates:
        return upload_fail(message='Image only!')

    file.save(f"app/{path}/{file.filename}")
    return f"/{path}/{file.filename}"


@app.route("/")
@app.route("/Популярное")
def top():
    top_list = VideoPosts.query.all()
    print(top_list)

    return render_template("index.html", is_user_authenticated=current_user.is_authenticated, videos_top=top_list,
                           resources=Resource, studios=Studios)


@login_required
@app.route('/Добавить видео', methods=['GET', 'POST'])
def add_video():
    studio_id = request.args.get("id")
    request_studio = Studios.query.filter_by(id=studio_id).first()

    if not current_user.is_authenticated or request_studio not in current_user.studios:
        return redirect("/")
    form = AddVideoForm()
    if form.validate_on_submit():
        video = Resource()
        video.format = form.video.data.filename.split(".")[-1]
        video.source = str(base64.b64encode(form.video.data.read()))[2:-1]
        db.session.add(video)
        db.session.commit()
        cover = Resource()

        cover.format = form.cover.data.filename.split(".")[-1]
        im = Image.open(form.cover.data)

        buffer = io.BytesIO()
        im.save(buffer, format=im.format)

        cover.source = str(base64.b64encode(buffer.getvalue()))[2:-1]
        db.session.add(cover)
        db.session.commit()

        video_post = VideoPosts()
        video_post.title = form.title.data
        video_post.description = form.description.data
        video_post.cover_id = cover.id
        video_post.source_id = video.id
        video_post.studio_id = studio_id
        db.session.add(video_post)
        db.session.commit()

        return redirect(url_for("show_studio", id=studio_id))
    return render_template('Добавить видео.html', is_user_authenticated=current_user.is_authenticated, title='Sign In',
                           form=form)


@login_required
@app.route('/Создать студию', methods=['GET', 'POST'])
def create_studio():
    if not current_user.is_authenticated:
        return redirect("/")
    form = CreateStudioForm()

    if form.validate_on_submit():
        cover = Resource()
        cover.format = form.cover.data.filename.split(".")[-1]

        cover.source = str(base64.b64encode(form.cover.data.read()))[2:-1]  # убираем ковычки
        db.session.add(cover)
        db.session.commit()

        studio = Studios()
        studio.title = form.title.data
        studio.description = form.description.data
        studio.cover_id = cover.id
        studio.user_id = current_user.id
        db.session.add(studio)
        db.session.commit()

        return redirect(url_for("show_studio", id=studio.id))
    return render_template('Создать студию.html', is_user_authenticated=current_user.is_authenticated, form=form)


@login_required
@app.route('/Мои студии')
def my_studios():
    if not current_user.is_authenticated:
        return redirect("/")
    studios = current_user.studios

    return render_template('Мои Студии.html', is_user_authenticated=current_user.is_authenticated, studios=studios,
                           resources=Resource)


@app.route('/Студия')
def show_studio():
    studio_id = request.args.get("id")
    st = Studios.query.get(studio_id)

    cover = Resource.query.get(st.cover_id)
    is_users_studio = False
    if current_user.is_authenticated and st in current_user.studios:
        is_users_studio = True

    return render_template('Студия.html', is_user_authenticated=current_user.is_authenticated,
                           is_users_studio=is_users_studio, cover=cover,
                           studio=st,
                           videos=st.videos,
                           resources=Resource)


@app.route('/Поиск видео')
def search_video():
    category = request.args.get("category")
    req = request.args.get("request")
    out_list = []
    if category == "string":
        out = []
        for word in req.split(" "):
            if len(word) > 1:
                # Title
                # out += VideoPosts.query.filter(VideoPosts.title.contains(word.lower())).all()
                # out += VideoPosts.query.filter(VideoPosts.title.contains(word.upper())).all()
                # out += VideoPosts.query.filter(VideoPosts.title.contains(word.title())).all()
                out += VideoPosts.query.filter(VideoPosts.title.contains(word)).all()
                # Description
                # out += VideoPosts.query.filter(VideoPosts.description.contains(word.lower())).all()
                # out += VideoPosts.query.filter(VideoPosts.description.contains(word.upper())).all()
                # out += VideoPosts.query.filter(VideoPosts.description.contains(word.title())).all()
                out += VideoPosts.query.filter(VideoPosts.description.contains(word)).all()
                # Studio
                studios_id = [studio.id for studio in Studios.query.filter(Studios.title.contains(word)).all()]

                out += VideoPosts.query.filter(VideoPosts.studio_id.in_(studios_id)).all()

        out_list = list(set(out))

    out_list.sort(key=lambda v: v.timestamp)
    return render_template('Поиск.html', is_user_authenticated=current_user.is_authenticated, studios=Studios,
                           resources=Resource,
                           list=out_list)


@app.route('/Видео')
def video():
    video_id = request.args.get("id")
    video_post = VideoPosts.query.get(video_id)

    video_source = Resource.query.get(video_post.source_id)
    cover_source = Resource.query.get(video_post.cover_id)
    studio = Studios.query.get(video_post.studio_id)
    studio_cover = Resource.query.get(studio.cover_id)
    return render_template("Видео.html", is_user_authenticated=current_user.is_authenticated, video=video_post,
                           studio=studio, studio_cover=studio_cover,
                           video_source=video_source, cover_source=cover_source)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404
