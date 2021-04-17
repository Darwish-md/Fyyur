#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# pylint: disable=no-member  
# pylint: disable=import-error
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ , and_
import logging, datetime
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate, MigrateCommand
import sys
from forms import ArtistForm, ShowForm, VenueForm
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    areas = db.session.query(Venue.city, Venue.state).all()
    for area in areas:
        venues_in_this_area = db.session.query(Venue).filter(and_(Venue.city == area.city, Venue.state == area.state)).all()
        for venue in venues_in_this_area:
            area["venues"].append({
            "id" : venue.id,
            "name" : venue.name,
            "num_upcoming_shows" : db.session.query(Venue, Show).join(Show).filter(Venue.id == venue.id, Show.start_time > datetime.today().date()).count()
            }) 
 
    return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term=request.form.get('search_term', '')
    responses = db.session.query(Venue, Artist).join(Artist).filter(or_(Venue.name.like('%' + search_term + '%'),Artist.name.like('%' + search_term + '%'))).all()
    i=1
    for response in responses:
        response["count"] = i
        response["num_upcoming_shows"] = db.session.query(Venue, Show).join(Show).filter(Venue.id == response["id"], Show.start_time > datetime.today().date()).count()
        i += 1
  
    return render_template('pages/search_venues.html', results=responses, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    data  = Venue.query.filter_by(id=venue_id).all().first()
    data["past_shows"] = db.session.query(Venue, Show, Artist.name.alias("artist_name"), Artist.image_link.alias("artist_image_link")).select_from(Venue).join(Show).join(Artist).filter(Venue.id == venue_id).all()
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
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link') 
        new_record = Venue(name=name,city=city,
        state=state, address=address,phone=phone, 
        genres=genres, image_link=image_link, 
        facebook_link=facebook_link)
        Venue.create(new_record)
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        if error:
            flash('An error occurred.It could not be listed.')
            return render_template('pages/home.html')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail
  error=False
  try:
      record_to_be_deleted = Venue.query.filter_by(id=venue_id)
      Venue.delete(record_to_be_deleted)
  except:
      db.session.rollback()
      print(sys.exc_info())
      error=True
  finally:
      if error:
          flash('An error occurred.It could not be deleted.')
          return render_template('pages/home.html')
      else:
          flash('Venue was deleted successfully')
          return render_template('pages/home.html')
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band"
  search_term=request.form.get('search_term', '')
  responses = db.session.query(Artist).filter(Artist.name.like('%' + search_term + '%')).all()
  j=1
  for response in responses:
      response["count"] = j
      response["num_upcoming_shows"] = db.session.query(Artist, Show).join(Show).filter(Artist.id == response["id"], Show.start_time > datetime.today().date()).count()
      j += 1

  return render_template('pages/search_artists.html', results=responses, search_term=search_term)

    
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.filter_by(artist_id=artist_id).all().first()
  artist_Shows_data= db.session.query(Artist, Venue.name.alias("venue_name"), Venue.image_link.alias("venue_image_link"),Show.venue_id, Show.artist_id, Show.start_time). \
  join(Show).join(Artist)
  artist["past_shows"] = artist_Shows_data.filter(Show.start_time < datetime.today().date()).all()
  artist["upcoming_shows"] = artist_Shows_data.filter(Show.start_time < datetime.today().date()).all()
  artist["past_shows_count"] = artist_Shows_data.filter(Show.start_time < datetime.today().date()).count()
  artist["upcoming_shows_count"] = artist_Shows_data.filter(Show.start_time > datetime.today().date()).count()

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.filter_by(id=artist_id).all().first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


""" 
1) user.no_of_logins += 1
   session.commit()

2) session.query().\
       filter(User.username == form.username.data).\
       update({"no_of_logins": (User.no_of_logins +1)})
   session.commit()

3) conn = engine.connect()
   stmt = User.update().\
       values(no_of_logins=(User.no_of_logins + 1)).\
       where(User.username == form.username.data)
   conn.execute(stmt)

4) setattr(user, 'no_of_logins', user.no_of_logins+1)
   session.commit()
"""

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    error = False  
    try:
        db.session.query(Artist).filter(Artist.id == artist_id).update({
        "name" : request.form.get('name'),
        "city" : request.form.get('city'),
        "state" : request.form.get('state'),
        "phone" : request.form.get('phone'),
        "genres" : request.form.get('genres'),
        "image_link" : request.form.get('image_link'),
        "facebook_link" : request.form.get('facebook_link')
        })
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True

    finally:
        if error:
            flash('An error occurred. It could not be edited.')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('Artist ' + request.form['name'] + ' was successfully edited!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.filter(id=venue_id).all().first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        db.session.query(Venue).filter(Venue.id == venue_id).update({
        "name" : request.form.get('name'),
        "city" : request.form.get('city'),
        "state" : request.form.get('state'),
        "address" : request.form.get('address'),
        "phone" : request.form.get('phone'),
        "genres" : request.form.get('genres'),
        "image_link" : request.form.get('image_link'),
        "facebook_link" : request.form.get('facebook_link'),
        })
        db.session.commit()
    
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True

    finally:
        if error:
            flash('An error occurred.It could not be edited.')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('Venue ' + request.form['name'] + ' was successfully edited!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        db.session.close()
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
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link') 
        new_record = Artist(name=name,city=city,
        state=state, phone=phone, 
        genres=genres, image_link=image_link, 
        facebook_link=facebook_link)
        Artist.create(new_record)
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        if error:
            flash('An error occurred. It could not be listed.')
            return render_template('pages/home.html')
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows_data = db.session.query(Venue.name.alias("venue_name"), Artist.name.alias("artist_name"),Artist.image_link.alias("artist_image_link"), Show.venue_id, Show.artist_id, Show.start_time). \
    join(Show).join(Artist).all()
    return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create', methods=['GET'])
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
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        new_show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        Show.create(new_show)
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        if error:
            flash('An error occurred. Show could not be listed.')
            return render_template('pages/home.html')
        else:
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        db.session.close()
        
        
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
