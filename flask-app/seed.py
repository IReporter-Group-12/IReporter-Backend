from faker import Faker
from models import db, CorruptionReport, CorruptionResolution, User, PetitionResolution, PublicPetition
from werkzeug.security import generate_password_hash
from app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
fake = Faker()

def seed_database():
    with app.app_context():
        # Delete existing data
        db.session.query(CorruptionResolution).delete()
        db.session.query(CorruptionReport).delete()
        db.session.query(PetitionResolution).delete()
        db.session.query(PublicPetition).delete()
        db.session.query(User).delete()
        db.session.commit()

        users = [
            User(fullname="Edith Chelangat", email="edith@example.com", password=bcrypt.generate_password_hash("Edit.123").decode('utf-8'), id_passport_no=12345678, role="citizen"),
            User(fullname="Rachael Njoki", email="rachael@example.com", password=bcrypt.generate_password_hash("@Ra1212049").decode('utf-8'), id_passport_no=23456789, role="admin"),
            User(fullname="Michelle Nasisiri", email="michelle@example.com", password=bcrypt.generate_password_hash("Michelle.123").decode('utf-8'), id_passport_no=34567890, role="admin"),
            User(fullname="Victor Muteithia", email="victor@example.com", password=bcrypt.generate_password_hash("Victor.123").decode('utf-8'), id_passport_no=45678901, role="citizen"),
            User(fullname="Victor Njoroge", email="victor2@example.com", password=bcrypt.generate_password_hash("Victor2.123").decode('utf-8'), id_passport_no=56789012, role="citizen"),
            User(fullname="Ann Irungu", email="ann@example.com", password=bcrypt.generate_password_hash("Ann.123").decode('utf-8'), id_passport_no=67890123, role="citizen")
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

        # Create sample corruption resolutions
        for report in CorruptionReport.query.all():
            resolution = CorruptionResolution(
                status=fake.random_element(elements=('Resolved', 'Under Investigation')),
                justification=fake.sentence(),
                additional_comments=fake.paragraph(),  
                record_id=report.id
            )
            db.session.add(resolution)

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

        # Create sample petition resolutions
        for petition in PublicPetition.query.all():
            resolution = PetitionResolution(
                status=fake.random_element(elements=('Resolved', 'Under Review')),
                justification=fake.sentence(),
                additional_comments=fake.paragraph(),  
                record_id=petition.id
            )
            db.session.add(resolution)

        db.session.commit()
        print("Done seeding!")

if __name__ == '__main__':
    with app.app_context():
        seed_database()


