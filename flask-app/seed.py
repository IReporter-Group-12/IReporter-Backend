from flask import Flask
from app import app  
from models import db, User, CorruptionReport, CorruptionResolution, PublicPetition, PetitionResolution



def seed_database():
    with app.app_context():
        # Create sample users
        user1 = User(fullname='John Doe', email='john@example.com', password='password1', id_passport_no=12345, role='admin')
        user2 = User(fullname='Jane Smith', email='jane@example.com', password='password2', id_passport_no=54321, role='user')
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create sample corruption reports
        report1 = CorruptionReport(govt_agency='Agency 1', county='County A', title='Report 1', description='Description 1', user_id=user1.id)
        report2 = CorruptionReport(govt_agency='Agency 2', county='County B', title='Report 2', description='Description 2', user_id=user2.id)
        db.session.add_all([report1, report2])
        db.session.commit()

        # Create sample corruption resolutions
        resolution1 = CorruptionResolution(status='Resolved', justification='Resolved the issue', record_id=report1.id)
        resolution2 = CorruptionResolution(status='Under Investigation', justification='Investigating the issue', record_id=report2.id)
        db.session.add_all([resolution1, resolution2])
        db.session.commit()

        # Create sample public petitions
        petition1 = PublicPetition(govt_agency='Agency X', county='County Y', title='Petition 1', description='Description 1', user_id=user1.id)
        petition2 = PublicPetition(govt_agency='Agency Y', county='County Z', title='Petition 2', description='Description 2', user_id=user2.id)
        db.session.add_all([petition1, petition2])
        db.session.commit()

        # Create sample petition resolutions
        petition_resolution1 = PetitionResolution(status='Resolved', justification='Resolved the petition', record_id=petition1.id)
        petition_resolution2 = PetitionResolution(status='Under Review', justification='Reviewing the petition', record_id=petition2.id)
        db.session.add_all([petition_resolution1, petition_resolution2])
        db.session.commit()

if __name__ == '__main__':
    seed_database()
