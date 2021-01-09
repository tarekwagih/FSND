#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import datetime
from os import name
import sys
import json
import dateutil.parser
import babel
from flask import ( 
    Flask, 
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
    jsonify 
    )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import FlaskForm
from forms import *
from pprint import pprint

from models import db, setup_db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    moment = Moment(app)
    #----------------------------------------------------------------------------#
    # Filters.
    #----------------------------------------------------------------------------#

    def format_datetime(value, format='medium'):
      date = dateutil.parser.parse(value)
      if format == 'full':
          format="EEEE MMMM, d, y 'at' h:mma"
      elif format == 'medium':
          format="EE MM, dd, y h:mma"
      return babel.dates.format_datetime(date, format)

    app.jinja_env.filters['datetime'] = format_datetime

    #----------------------------------------------------------------------------#
    # Controllers.
    #----------------------------------------------------------------------------#

    @app.route('/')
    def index():
      return render_template('pages/home.html')

    #  Venues
    #  ----------------------------------------------------------------

    @app.route('/venues')
    def venues():
      # TODO: replace with real venues data.
      # num_shows should be aggregated based on number of upcoming shows per venue.
      
      city_groub = db.session.query(Venue).distinct(Venue.state, Venue.city).all()

      data = []
      
      for city_l in city_groub:
            val_dic = {}
            venues = db.session.query(Venue).group_by(Venue.id, Venue.city, Venue.state).all()
            for venue in venues:
                  if venue.city == city_l.city:
                        val_dic['city'] = city_l.city
                        val_dic['state'] = city_l.state
                  venue_i = db.session.query(Venue).filter(Venue.city == city_l.city).all()
                  ven_ls = []
                  for ven_last in venue_i:
                      ven_ls.append(ven_last)
                  val_dic['venues'] = ven_ls
            data.append(val_dic)  

      return render_template('pages/venues.html', areas=data)

    @app.route('/venues/search', methods=['POST'])
    def search_venues():
      # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
      # seach for Hop should return "The Musical Hop".
      # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
      searsh_tearm = request.form.get('search_term')
      search_like = "%{}%".format(searsh_tearm)
      response = db.session.query(Venue).filter(Venue.name.ilike(search_like)).all()
      count = db.session.query(Venue).filter(Venue.name.ilike(search_like)).count()
      return render_template('pages/search_venues.html', results=response, count=count, search_term=request.form.get('search_term', ''))

    @app.route('/venues/<int:venue_id>')
    def show_venue(venue_id):
      # shows the venue page with the given venue_id
      # TODO: replace with real venue data from the venues table, using venue_id

      venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
        
      past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
          filter(
              Show.venue_id == venue_id,
              Show.artist_id == Artist.id,
              Show.date < datetime.now()
          ).\
          all() 
      upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
          filter(
          Show.venue_id == venue_id,
          Show.artist_id == Artist.id,
          Show.date > datetime.now()
      ).\
          all()
          
      data = {
          'id': venue.id,
          'name': venue.name,
          'city' : venue.city,
          'state' : venue.state,
          'address': venue.address,
          'phone' : venue.phone,
          'genres': list(venue.genres),
          'image_link' : venue.image_link,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'seeking_description': venue.seeking_description,
          'past_shows': [{
              'artist_id': artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": show.date.strftime("%m/%d/%Y, %H:%M")
          } for artist, show in past_shows],
          'upcoming_shows': [{
              'artist_id': artist.id,
              'artist_name': artist.name,
              'artist_image_link': artist.image_link,
              'start_time': show.date.strftime("%m/%d/%Y, %H:%M")
          } for artist, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
      }

      return render_template('pages/show_venue.html', venue=data)

    #  Create Venue
    #  ----------------------------------------------------------------

    @app.route('/venues/create', methods=['GET'])
    def create_venue_form():
      form = VenueForm()
      return render_template('forms/new_venue.html', form=form)

    @app.route('/venues/create', methods=['POST'])
    def create_venue_submission():
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      error = False
      try:
        # insert & Commit
        form = VenueForm(request.form)
        
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website=form.website.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
            genres=list(form.genres.data)
        )
        db.session.add(venue)
        db.session.commit()
      except:
        # error Or Not
        error = True
        db.session.rollback()
        print(sys.exc_info()) 
      finally:
        # dissmis
        db.session.close()
      if error:
            abort (400)
      else:
      # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')


    @app.route('/venues/<int:venue_id>', methods=['DELETE'])
    def delete_venue(venue_id):
      # TODO: Complete this endpoint for taking a venue_id, and using
      # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
      error = False
      try:
        # db.session.query(Venue).filter(id=venue_id).delete()
        Show.query.filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
      except:
        error = True
        db.session.rollback()
        print(sys.exc_info()) 
      finally:
        db.session.close()
      # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
      # clicking that button delete it from the db then redirect the user to the homepage
      if error:
          abort(400)
      else:
        flash('Venue was successfully Deleted!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')

    #  Artists
    #  ----------------------------------------------------------------
    @app.route('/artists')
    def artists():
      # TODO: replace with real data returned from querying the database  
      data = db.session.query(Artist).all()
      return render_template('pages/artists.html', artists=data)

    @app.route('/artists/search', methods=['POST'])
    def search_artists():
      # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
      # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
      # search for "band" should return "The Wild Sax Band".
      searsh_tearm = request.form.get('search_term')
      search_like = "%{}%".format(searsh_tearm)
      response = db.session.query(Artist).filter(Artist.name.ilike(search_like)).all()
      count = db.session.query(Artist).filter(Artist.name.ilike(search_like)).count()
      return render_template('pages/search_artists.html', results=response, count=count , search_term=request.form.get('search_term', ''))

    @app.route('/artists/<int:artist_id>')
    def show_artist(artist_id):
      # shows the venue page with the given venue_id
      # TODO: replace with real venue data from the venues table, using venue_id

      artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

      past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
          filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.date < datetime.now()
      ).\
          all()
      upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
          filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.date > datetime.now()
      ).\
          all()

      data = {
          'id': artist.id,
          'name': artist.name,
          'city': artist.city,
          'state': artist.state,
          'phone': artist.phone,
          'genres': artist.genres,
          'image_link': artist.image_link,
          'facebook_link': artist.facebook_link,
          'seeking_venue': artist.seeking_venue,
          'seeking_description': artist.seeking_description,
          'past_shows': [{
              'venue_id': venue.id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": show.date.strftime("%m/%d/%Y, %H:%M")
          } for venue, show in past_shows],
          'upcoming_shows': [{
              'venue_id': venue.id,
              'venue_name': venue.name,
              'venue_image_link': venue.image_link,
              'start_time': show.date.strftime("%m/%d/%Y, %H:%M")
          } for venue, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
      }

      return render_template('pages/show_artist.html', artist=data)

    #  Update
    #  ----------------------------------------------------------------
    @app.route('/artists/<int:artist_id>/edit', methods=['GET'])
    def edit_artist(artist_id):
      form = ArtistForm()
      
      # TODO: populate form with fields from artist with ID <artist_id>
      artist= db.session.query(Artist).filter(Artist.id==artist_id).first()
      return render_template('forms/edit_artist.html', form=form, artist=artist)

    @app.route('/artists/<int:artist_id>/edit', methods=['POST'])
    def edit_artist_submission(artist_id):
      # TODO: take values from the form submitted, and update existing
      # artist record with ID <artist_id> using the new attributes
      error = False
      try:
        # update & Commit
        artist = db.session.query(Artist).get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        artist.seeking_venue = request.form['seeking_venue']
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
      except:
        # error Or Not
        error = True
        db.session.rollback()
        print(sys.exc_info())
      finally:
        # dissmis
        db.session.close()
      if error:
          abort(400)
      else:
          # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully Updated!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return redirect(url_for('show_artist', artist_id=artist_id))

    @app.route('/venues/<int:venue_id>/edit', methods=['GET'])
    def edit_venue(venue_id):
      form = VenueForm()
      
      # TODO: populate form with values from venue with ID <venue_id>
      venue = db.session.query(Venue).filter(Venue.id == venue_id).first()

      return render_template('forms/edit_venue.html', form=form, venue=venue)

    @app.route('/venues/<int:venue_id>/edit', methods=['POST'])
    def edit_venue_submission(venue_id):
      # TODO: take values from the form submitted, and update existing
      # venue record with ID <venue_id> using the new attributes
      error = False
      try:
        # update & Commit
        venue = db.session.query(Venue).get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.seeking_talent = request.form['seeking_talent']
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
      except:
        # error Or Not
        error = True
        db.session.rollback()
        print(sys.exc_info())
      finally:
        # dissmis
        db.session.close()
      if error:
          abort(400)
      else:
          # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully Updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))

    #  Create Artist
    #  ----------------------------------------------------------------

    @app.route('/artists/create', methods=['GET'])
    def create_artist_form():
      form = ArtistForm()
      return render_template('forms/new_artist.html', form=form)

    @app.route('/artists/create', methods=['POST'])
    def create_artist_submission():
      # called upon submitting the new artist listing form
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      error = False
      try:
        # insert & Commit
        form = ArtistForm(request.form)

        artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website=form.website.data,
          seeking_description=form.seeking_description.data,
          seeking_venue=form.seeking_venue.data
        )
        db.session.add(artist)
        db.session.commit()
      except:
        # error Or Not
        error = True
        db.session.rollback()
        print(sys.exc_info()) 
      finally:
        # dissmis
        db.session.close()
      if error:
        abort (400)
      else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

    #  Shows
    #  ----------------------------------------------------------------

    @app.route('/shows')
    def shows():
      # displays list of shows at /shows
      # TODO: replace with real venues data.
      # num_shows should be aggregated based on number of upcoming shows per venue.

      shows = db.session.query(Venue, Artist, Show).\
        select_from(Show).\
        join(Artist).\
        join(Venue).\
          filter(
          Show.artist_id == Artist.id,
          Show.venue_id == Venue.id,
      ).\
        all()

      data = [{
              'venue_id': venue.id,
              "venue_name": venue.name,
              'artist_id': artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": show.date.strftime("%m/%d/%Y, %H:%M")
          } for venue, artist, show in shows]
      
      return render_template('pages/shows.html', shows=data)

    @app.route('/shows/create')
    def create_shows():
      # renders form. do not touch.
      form = ShowForm()
      return render_template('forms/new_show.html', form=form)

    @app.route('/shows/create', methods=['POST'])
    def create_show_submission():
      # called to create new shows in the db, upon submitting new show listing form
      # TODO: insert form data as a new Show record in the db, instead
      error = False
      try:
        # insert & Commit
        form = ShowForm(request.form)

        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            date=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
      except:
        # error Or Not
        error = True
        db.session.rollback()
        print(sys.exc_info())
      finally:
        # dissmis
        db.session.close()

      if error:
        abort(400)
      else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')

      # on successful db insert, flash success
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      # return render_template('pages/home.html')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500


    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')
        
    return app



#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

app = create_app()


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
