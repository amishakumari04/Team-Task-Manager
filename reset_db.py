from models import SessionLocal, User, Project, Task, engine, Base

def reset_now():
    # This drops all tables and recreates them empty
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database has been cleared successfully!")

if __name__ == "__main__":
    reset_now()