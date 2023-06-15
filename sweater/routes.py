from io import BytesIO
from flask import render_template, redirect, url_for, request, flash, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from sweater.models import Employees, Profile, Message, Aviary, Cleaning,\
    Animals, Medical_card, Water_treatments, \
    Food, Upload
from sweater import app, db


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg', 'gif'}

@app.route("/")
def index():
    return render_template("index.html", title="Главная")


@app.route("/authorization", methods=['GET', 'POST'])
def authorization():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = Employees.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile', nickname=login))
        else:
            flash("Данные неверны", category="error")
    else:
        pass
    return render_template("authorization.html", title="Авторизация")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/enter")
def enter():
    return redirect(url_for('profile'))


@app.route("/profile/<nickname>", methods=['GET', 'POST'])
@login_required
def profile(nickname):
    personal = Employees.query.filter_by(login=nickname).all()
    print(personal)
    return render_template("profile.html", title="Профиль", personal=personal)


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    return render_template('admin.html', title="Админ")


@app.route("/staff/<alias>", methods=['GET', 'POST'])
@login_required
def staff(alias):
    animal = Animals.query.filter_by(type=alias).all()
    messages = Message.query.filter_by(animal_id=animal[0].id).all()
    list_cleaning = Cleaning.query.filter_by(aviary_id=animal[0].aviary.animal_id).all()
    list_food = Food.query.filter_by(animal_id=animal[0].id).all()
    list_water = Water_treatments.query.filter_by(animal_id=animal[0].id).all()

    if request.method == 'POST':
        try:
            clean = Cleaning(aviary_id=animal[0].aviary.animal_id, date_clean=request.form['date_clean'],
                             time_clean=request.form['time_clean'])
            if clean.date_clean != '' and clean.time_clean != '':
                db.session.add(clean)
                db.session.commit()

            food = Food(animal_id=animal[0].id,
                        date_food=request.form['date_food'],
                        time_food=request.form['time_food'])
            if food.date_food != '' and food.time_food != '':
                db.session.add(food)
                db.session.commit()

            water = Water_treatments(animal_id=animal[0].id,
                                     date_of_procedures=request.form['date_of_procedures'],
                                     time_water=request.form['time_water'])
            if water.date_of_procedures != '' and water.time_water != '':
                db.session.add(water)
                db.session.commit()

            flash('Отчёт успешно загружен', category='success')
            print("Информация успешно добавлена")
        except Exception as e:
            db.session.rollback()
            flash('Ошибка добавления в базу данных')
            print("Ошибка добавления в БД")
            print(e)

    return render_template('staff.html', title="Обслуживающий персонал",
                           messages=messages, list_cleaning=list_cleaning[-2:],
                           list_food=list_food[-2:], list_water=list_water[-2:],
                           animal=animal[0])

@app.route("/animals", methods=['GET', 'POST'])
@login_required
def animals():
    list_of_animal = Animals.query.all()
    if not list_of_animal:
        return "Животных нет"
    return render_template('animals.html', title="Список животных", list_of_animal=list_of_animal)


@app.route("/animal/<alias>", methods=['GET', 'POST'])
@login_required
def animal(alias):
    concrete_animal = Animals.query.filter_by(type=alias).all()
    temp = concrete_animal[0].id
    url = current_user.url[1:]
    download = Upload.query.filter_by(animal_id=temp)
    messages = Message.query.filter_by(animal_id=concrete_animal[0].id).all()

    if request.method == 'POST':
        try:
            file = request.files['download_file']

            u = Upload(filename=file.filename, data=file.read(), animal_id=concrete_animal[0].id)
            if u.filename != '':
                Upload.query.filter_by(animal_id=concrete_animal[0].id).delete()
                db.session.commit()

                db.session.add(u)
                db.session.commit()

            m = Message(text=request.form['text'], animal_id=concrete_animal[0].id)
            if m.text != '':
                db.session.add(m)
                db.session.commit()

            delete = request.form['delete']
            del_mes = Message.query.filter_by(id=delete).first()
            if del_mes:
                db.session.delete(del_mes)
                db.session.commit()

            flash("Информация успешно добавлена")
            print("Информация успешно добавлена")

        except Exception as e:
            db.session.rollback()
            print("Ошибка добавления в БД")
            flash("Ошибка добавления в БД")
            print(e)

    return render_template('animal.html', title=alias,
                           concrete_animal=concrete_animal,
                           user=current_user, url=url,
                           download=download, temp=temp,
                           messages=messages)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        try:
            hash = generate_password_hash(request.form['password'])
            e = Employees(email=request.form['email'],
                          login=request.form['login'],
                          password=hash, url='/' + request.form['url'])
            db.session.add(e)
            db.session.flush()

            p = Profile(surname=request.form['surname'],
                        name=request.form['name'],
                        patronymic=request.form['patronymic'],
                        date_of_birth=request.form['date_of_birth'],
                        telephone=request.form['telephone'],
                        address=request.form['address'],
                        date_of_admission=request.form['date_of_admission'],
                        post=request.form['post'],
                        employee_id=e.id)
            db.session.add(p)
            db.session.commit()

            flash("Пользователь успешно загружен", category="success")

        except Exception as e:
            flash("Ошибка добавления в БД", category="error")
            db.session.rollback()
            print("Ошибка добавления в БД")
            print(e)

    return render_template('register.html')


@app.route('/new_animal', methods=['GET', 'POST'])
@login_required
def new_animal():
    if request.method == 'POST':
        try:
            an = Animals(date_of_receipt=request.form['date_of_receipt'],
                         type=request.form['type'],
                         description=request.form['description'],
                         status=request.form['status'])

            db.session.add(an)
            db.session.flush()

            av = Aviary(size=request.form['size'], type=request.form['type_aviary'],
                        features=request.form['features'], animal_id=an.id)

            db.session.add(av)
            db.session.flush()

            mc = Medical_card(gender=request.form['gender'],
                              weight=request.form['weight'],
                              height=request.form['height'],
                              special_signs=request.form['special_signs'],
                              health_status=request.form['health_status'],
                              animal_id=an.id)

            db.session.add(mc)
            db.session.flush()

            file = request.files['upload_file']

            u = Upload(filename=file.filename, data=file.read(), animal_id=an.id)
            db.session.add(u)
            db.session.commit()

            flash("Животное успешно добавлено", category="success")

        except Exception as e:
            db.session.rollback()
            flash("Ошибка добавления в БД", category="error")
            print("Ошибка добавления в БД")
            print(e)

    return render_template('new_animal.html', title='Добавление новых животных')


@app.route('/download/<upload_id>')
@login_required
def download(upload_id):
    upload = Upload.query.filter_by(animal_id=upload_id).first()
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)


@app.route('/delete_animal', methods=['GET', 'POST'])
@login_required
def delete_animal():
    list_of_animal = Animals.query.all()
    if request.method == 'POST':
        try:
            animal = request.form['animal']
            choose_animal = Animals.query.filter_by(type=animal).first()
            lst = [choose_animal, choose_animal.aviary,
                   choose_animal.medical_card,
                   choose_animal.water_treatments[0],
                   choose_animal.food[0],
                   choose_animal.upload[0]]


            for item in lst:
                if item:
                    db.session.delete(item)
                    db.session.flush()
            db.session.commit()
            flash("Животное успешно удалено", category="success")
            print("Животное удалено")

        except Exception as e:
            db.session.rollback()
            flash("Ошибка удаления из БД", category="error")
            print("Ошибка удаления из БД")
            print(e)

    return render_template('deleting_animals.html', title="Удаление животных", list_of_animal=list_of_animal)


@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    list_of_users = Employees.query.all()
    if request.method == 'POST':
        try:
            login = request.form['login']
            user = Employees.query.filter_by(login=login).first()
            print(user)
            print(user.pr)
            db.session.delete(user)
            db.session.delete(user.pr)
            db.session.commit()
            flash("Пользователь успешно удалён", category="success")
            print("Пользователь успешно удалён")

        except Exception as e:
            db.session.rollback()
            flash("Ошибка удаления из БД", category="error")
            print("Ошибка удаления из БД")
            print(e)

    return render_template('users.html', title="Удаление пользователей", list_of_users=list_of_users)


@app.route('/profiles_employees', methods=['POST', 'GET'])
def profiles_employees():
    list_of_users = Employees.query.all()
    return render_template('profiles_employees.html', title='Профили работников', list_of_users=list_of_users)
