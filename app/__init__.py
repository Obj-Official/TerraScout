from . import models, database

# This line ensures that all SQLAlchemy models (User, Message) 
# are loaded and their metadata is registered with the Base class.
# It then checks the database file and creates the tables if they don't exist.
models.Base.metadata.create_all(bind=database.engine)