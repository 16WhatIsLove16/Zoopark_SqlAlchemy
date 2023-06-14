from flask_login import UserMixin

from sweater import db, manager

class Employees(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    login = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(500), nullable=True)
    date = db.Column(db.Text)
    url = db.Column(db.String, nullable=True)

    pr = db.relationship('Profile', backref='employees', uselist=False)

    def __repr__(self):
        return "<employees %r>" % self.id


profiles_aviary = db.Table(
    'profile_aviary',
    db.Column('profile.id', db.ForeignKey('profile.id'), primary_key=True),
    db.Column('aviary.id', db.ForeignKey('aviary.id'), primary_key=True),
)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    patronymic = db.Column(db.String(50))
    date_of_birth = db.Column(db.Text)
    telephone = db.Column(db.Integer)
    address = db.Column(db.String(100))
    date_of_admission = db.Column(db.Text)
    Date_of_dismissal = db.Column(db.Text)
    post = db.Column(db.String(50))

    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), unique=True)

    following = db.relationship('Aviary', secondary=profiles_aviary, backref='profile')

    def __repr__(self):
        return f"<profiles {self.id}>"


class Aviary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.Integer, nullable=True)
    type = db.Column(db.Text, nullable=True)
    features = db.Column(db.Text, nullable=True)

    cleaning = db.relationship('Cleaning', backref='aviary', lazy='dynamic')
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))


class Cleaning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_clean = db.Column(db.Text)
    time_clean = db.Column(db.Text)

    aviary_id = db.Column(db.Integer, db.ForeignKey('aviary.id'))


class Animals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_receipt = db.Column(db.Text)
    type = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)

    aviary = db.relationship('Aviary', backref='animals', uselist=False)
    medical_card = db.relationship('Medical_card', backref='animals', uselist=False)
    water_treatments = db.relationship('Water_treatments', backref='animals')
    # vaccination = db.relationship('Vaccination', backref='animals')
    # wellness = db.relationship('Wellness_activities', backref='animals')
    food = db.relationship('Food', backref='animals')
    upload = db.relationship('Upload', backref='animals')
    message = db.relationship('Message', backref='animals')


class Medical_card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    special_signs = db.Column(db.Text, nullable=True)
    health_status = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)

    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))

    # vaccination = db.relationship('Vaccination', backref='medical_card')
    food = db.relationship('Food', backref='medical_card')


class Water_treatments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_procedures = db.Column(db.Text)
    time_water = db.Column(db.Text)

    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))


# class Vaccination(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name_vaccination = db.Column(db.Text, nullable=True)
#     date_vaccination = db.Column(db.Text)
#     time = db.Column(db.Text)
#
#     animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))
#     vac = db.Column(db.Integer, db.ForeignKey('medical_card.id'))


# class Wellness_activities(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name_activities = db.Column(db.Text, nullable=True)
#     data = db.Column(db.Text)
#     time = db.Column(db.Text)
#
#     animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_food = db.Column(db.Text)
    time_food = db.Column(db.Text)

    medical_card_id = db.Column(db.Integer, db.ForeignKey('medical_card.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)

    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024))

    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))


@manager.user_loader
def load_user(user_id):
    return Employees.query.get(user_id)
