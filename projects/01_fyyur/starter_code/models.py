import babel
from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

def setup_db(app):
    db.app = app
    db.init_app(app)
    app.config.from_object('config')
    db.create_all()
    migrate = Migrate(app, db)




#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Integer, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    
    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    show_id = db.relationship('Show', backref='Venue', cascade="all, delete-orphan", lazy=True)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Integer, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)

    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    show_id = db.relationship('Show', backref='Artist', cascade="all, delete-orphan", lazy=True)


# TODO Implement Show Model
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    date = db.Column(db.DateTime, default=babel.dates.format_datetime(), nullable=False)
