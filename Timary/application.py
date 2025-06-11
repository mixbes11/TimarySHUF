import os
from datetime import date, time, timedelta

from flask import (
    Flask,
    redirect,
    render_template,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from Timary.data import db_session
from Timary.data.models import Homework, Timetable, User
from Timary.forms import (
    ChangeForm,
    HomeworkForm,
    LoginForm,
    RegisterForm,
    TimetableForm,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "very_secret_key_jwkjldjwkdjlkwdkwjdldwhifwifhwiuhiuefhwiufhiuehf0f9wwefw"
)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    return user


@app.route("/")
def index():
    today = date.today().isoformat()
    return redirect(f"/timetable/{today}")


@app.route("/timetable/<date_str>")
def index_start(date_str):
    if current_user.is_anonymous:
        return render_template("main.html", len_task=0)

    try:
        current_date = date.fromisoformat(date_str)
    except ValueError:
        return redirect("/")

    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    db = db_session.create_session()
    lessons = (
        db.query(Timetable)
        .filter(
            Timetable.id == current_user.id,
            Timetable.date >= start_of_week,
            Timetable.date <= end_of_week,
        )
        .order_by(Timetable.date, Timetable.time)
        .all()
    )

    days = {}
    weekdays = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_name = weekdays[i]
        days[day_name] = {"date": day_date.strftime("%d.%m.%Y"), "lessons": []}

    for lesson in lessons:
        day_name = weekdays[lesson.date.weekday()]
        days[day_name]["lessons"].append(lesson)

    previous_week_date = (start_of_week - timedelta(days=7)).isoformat()
    next_week_date = (start_of_week + timedelta(days=7)).isoformat()

    db.close()
    return render_template(
        "main.html",
        days=days,
        len_lesson=len(lessons),
        previous_week_date=previous_week_date,
        next_week_date=next_week_date,
    )


@app.route("/homework/")
@login_required
def homework_default():
    today = date.today().isoformat()
    return redirect(f"/homework/{today}")


@app.route("/homework/<date_str>")
def homework(date_str):
    if current_user.is_anonymous:
        return render_template("homework.html", len_task=0)

    try:
        current_date = date.fromisoformat(date_str)
    except ValueError:
        today = date.today().isoformat()
        return redirect(f"/homework/{today}")

    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    db = db_session.create_session()
    tasks = (
        db.query(Homework)
        .filter(
            Homework.id == current_user.id,
            Homework.date >= start_of_week,
            Homework.date <= end_of_week,
        )
        .order_by(Homework.date)
        .all()
    )

    days = {}
    weekdays = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_name = weekdays[i]
        days[day_name] = {"date": day_date.strftime("%d.%m.%Y"), "tasks": []}

    for task in tasks:
        day_name = weekdays[task.date.weekday()]
        days[day_name]["tasks"].append(task)

    previous_week_date = (start_of_week - timedelta(days=7)).isoformat()
    next_week_date = (start_of_week + timedelta(days=7)).isoformat()

    db.close()
    return render_template(
        "homework.html",
        days=days,
        len_task=len(tasks),
        previous_week_date=previous_week_date,
        next_week_date=next_week_date,
    )


@app.route("/register", methods=["GET", "POST"])
def reqister():
    if current_user.is_authenticated:
        return redirect("/")
    form = RegisterForm()
    if form.password.data and form.login.data and form.name.data and form.email.data:
        if form.validate_on_submit():
            if len(form.password.data) < 6:
                return render_template(
                    "register.html",
                    form=form,
                    message="Пароль должен содержать не меньше 6 символов",
                )
            if form.password.data.isdigit() or form.password.data.isalpha():
                return render_template(
                    "register.html",
                    form=form,
                    message="Пароль должен состоять не только из букв или цифр",
                )
            if not form.login.data or not form.name.data or not form.email.data:
                return render_template(
                    "register.html",
                    form=form,
                    message="Проверьте правильность заполнения полей",
                )
            db = db_session.create_session()
            if (
                db.query(User).filter(User.email == form.email.data).first()
                or db.query(User).filter(User.login == form.login.data).first()
            ):
                return render_template(
                    "register.html",
                    form=form,
                    message="Такой пользователь уже существует",
                )
            user = User(
                login=form.login.data,
                name=form.name.data,
                email=form.email.data,
                theme="1",
            )
            user.set_password(form.password.data)
            db.add(user)
            db.commit()
            login_user(user, remember=True)
            db.close()
            return redirect("/user_info")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    login_form = LoginForm()
    if login_form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(User.login == login_form.login.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=True)
            db.close()
            return redirect("/user_info")
        db.close()
        return render_template(
            "login.html", form1=login_form, message1="Неправильный логин или пароль"
        )
    return render_template("login.html", form1=login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/user_info")
@login_required
def user_info():
    return render_template("user_info.html")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    all_data = {
        "login": current_user.login,
        "name": current_user.name,
        "email": current_user.email,
    }
    change_form = ChangeForm(data=all_data)
    if change_form.validate_on_submit():
        db = db_session.create_session()
        password = change_form.password.data
        user_now = db.query(User).filter(User.id == current_user.id).first()
        if user_now.check_password(password):
            user_now.login = change_form.login.data
            user_now.name = change_form.name.data
            emails = db.query(User).filter(User.email == change_form.email.data).all()
            if len(emails) >= 2 and emails[0] != user_now.email:
                db.close()
                return render_template(
                    "change.html",
                    form=change_form,
                    message="Такая почта уже используется в другом аккаунте",
                )
            else:
                user_now.email = change_form.email.data
            db.commit()
            db.close()
            return redirect("/user_info")
        else:
            return render_template(
                "change.html", form=change_form, message="Неправильный пароль"
            )
    return render_template("change.html", form=change_form)


@app.route("/add_timetable/<int:id>", methods=["GET", "POST"])
@login_required
def add_timetable(id):
    if id != 0:
        db = db_session.create_session()
        lesson = db.query(Timetable).filter(Timetable.lesson_id == int(id)).first()
        if not lesson or lesson.user != current_user:
            db.close()
            return redirect("/")

        all_data = {
            "lesson": lesson.lesson,
            "room": lesson.room,
            "date": lesson.date,
        }
        if lesson.time is not None:
            all_data["hour"] = lesson.time.hour
            all_data["minute"] = lesson.time.minute

        timetable_form = TimetableForm(data=all_data)
        if timetable_form.validate_on_submit():
            lesson.lesson = timetable_form.lesson.data
            lesson.room = timetable_form.room.data
            lesson.date = timetable_form.date.data
            lesson.time = time(
                hour=timetable_form.hour.data, minute=timetable_form.minute.data
            )
            db.commit()
            target_date = lesson.date.isoformat()
            db.close()
            return redirect(f"/timetable/{target_date}")
        db.close()
        return render_template(
            "add_timetable.html", form=timetable_form, deletion=True, id=id
        )
    else:
        timetable_form = TimetableForm()
        if timetable_form.validate_on_submit():
            db = db_session.create_session()
            timetable = Timetable()
            timetable.id = current_user.id
            timetable.lesson = timetable_form.lesson.data
            timetable.room = timetable_form.room.data
            timetable.date = timetable_form.date.data
            if (
                timetable_form.hour.data is not None
                and timetable_form.minute.data is not None
            ):
                timetable.time = time(
                    hour=timetable_form.hour.data, minute=timetable_form.minute.data
                )
            else:
                timetable.time = None
            db.add(timetable)
            db.commit()
            target_date = timetable.date.isoformat()
            db.close()
            return redirect(f"/timetable/{target_date}")
        return render_template(
            "add_timetable.html", form=timetable_form, deletion=False
        )


@app.route("/delete_timetable/<int:id>")
@login_required
def delete_timetable(id):
    db = db_session.create_session()
    lesson = (
        db.query(Timetable)
        .filter(Timetable.user == current_user, Timetable.lesson_id == id)
        .first()
    )
    if lesson and lesson.user == current_user:
        target_date = lesson.date.isoformat()
        db.delete(lesson)
        db.commit()
        db.close()
        return redirect(f"/timetable/{target_date}")
    db.close()
    return redirect("/")


@app.route("/add_homework/<int:id>", methods=["GET", "POST"])
@login_required
def add_homework(id):
    if id != 0:
        db = db_session.create_session()
        task = db.query(Homework).filter(Homework.homework_id == int(id)).first()
        if not task or task.user != current_user:
            db.close()
            return redirect(f"/homework/{date.today().isoformat()}")
        all_data = {
            "task": task.task,
            "lesson": task.lesson,
            "date": task.date,
            "ready": task.ready,
        }
        homework_form = HomeworkForm(data=all_data)
        if homework_form.validate_on_submit():
            task.task = homework_form.task.data
            task.lesson = homework_form.lesson.data
            task.date = homework_form.date.data
            task.ready = homework_form.ready.data
            db.commit()
            target_date = task.date.isoformat()
            db.close()
            return redirect(f"/homework/{target_date}")
        db.close()
        return render_template(
            "add_homework.html", form=homework_form, deletion=True, id=id
        )
    else:
        homework_form = HomeworkForm()
        if homework_form.validate_on_submit():
            db = db_session.create_session()
            homework = Homework()
            homework.task = homework_form.task.data
            homework.lesson = homework_form.lesson.data
            homework.date = homework_form.date.data
            homework.ready = homework_form.ready.data
            homework.file = homework_form.file.data
            current_user.homework.append(homework)
            db.merge(current_user)
            db.commit()
            target_date = homework.date.isoformat()
            db.close()
            return redirect(f"/homework/{target_date}")
        return render_template("add_homework.html", form=homework_form, deletion=False)


@app.route("/delete_homework/<int:id>")
@login_required
def delete_homework(id):
    db = db_session.create_session()
    task = (
        db.query(Homework)
        .filter(Homework.user == current_user, Homework.homework_id == id)
        .first()
    )
    if task and task.user == current_user:
        target_date = task.date.isoformat()
        db.delete(task)
        db.commit()
        db.close()
        return redirect(f"/homework/{target_date}")
    db.close()
    return redirect(f"/homework/{date.today().isoformat()}")


"""
@app.errorhandler(404)
def not_found(error):
    if current_user.is_authenticated:
        info = (current_user.name + ' ' + current_user.surname)
    else:
        info = 'Anonymous'
    er_txt = '404 not found: Такого адреса не существует'
    return render_template('error.html',
                           text=er_txt, useracc=info)



@app.errorhandler(401)
def unauth(error):
    er_txt = '401 not authorized: Пожалуйста, авторизуйтесь на сайте!'
    return render_template('error.html', text=er_txt)


@app.errorhandler(500)
def error_serv(error):
    er_text = 'Кажется, на сервере возникла ошибка. Выйдите на главную страницу и попробуйте снова'
    return render_template('error.html', text=er_text)
"""

from os import path

db_session.global_init(path.join(path.dirname(__file__), "./db/project.db"))


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
