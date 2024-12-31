print("Starting database initialization...")

from database import Base, engine
import models

# Create tables in the database
Base.metadata.create_all(bind=engine)
print("Database initialized and tables created.")
