from faker import Faker
from models import db, CorruptionReport, User, PublicPetition
from app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
fake = Faker()

def seed_database():
    with app.app_context():
        # Delete existing data
        db.session.query(CorruptionReport).delete()
        db.session.query(PublicPetition).delete()
        db.session.query(User).delete()
        db.session.commit()

        users = [
            User(fullname="Edit Chelangat", email="edith@example.com", password=bcrypt.generate_password_hash("Edith.123").decode('utf-8'), id_passport_no=12345678, role="user"),
            User(fullname="Rachael Njoki", email="rachael@example.com", password=bcrypt.generate_password_hash("@Ra1212049").decode('utf-8'), id_passport_no=23456789, role="admin"),
            User(fullname="Michelle Nasirisi", email="michelle@example.com", password=bcrypt.generate_password_hash("Michelle.123").decode('utf-8'), id_passport_no=34567890, role="admin"),
            User(fullname="Victor Muteithia", email="victorm@example.com", password=bcrypt.generate_password_hash("VictorM.123").decode('utf-8'), id_passport_no=45678901, role="user"),
            User(fullname="Victor Njoroge", email="victorn@example.com", password=bcrypt.generate_password_hash("VictorN.123").decode('utf-8'), id_passport_no=56789012, role="admin"),
            User(fullname="Ann Irungu", email="ann@example.com", password=bcrypt.generate_password_hash("Ann.123").decode('utf-8'), id_passport_no=67890123, role="user")
        ]
        
        db.session.add_all(users)
        db.session.commit()    

       
        # Create sample corruption reports
        for _ in range(10):  # Generate 10 corruption reports
            report = CorruptionReport(
                govt_agency=fake.company(),
                county=fake.city(),
                title=fake.sentence(),
                description=fake.paragraph(),
                user_id=fake.random_element(elements=User.query.all()).id
            )
            db.session.add(report)

        db.session.commit()


        # Create sample public petitions
        for _ in range(5):  # Generate 5 public petitions
            petition = PublicPetition(
                govt_agency=fake.company(),
                county=fake.city(),
                title=fake.sentence(),
                description=fake.paragraph(),
                user_id=fake.random_element(elements=User.query.all()).id
            )
            db.session.add(petition)

        db.session.commit()

        print("Done seeding!")

if __name__ == '__main__':
    seed_database()

