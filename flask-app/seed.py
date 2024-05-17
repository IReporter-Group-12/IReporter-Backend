from flask import Flask
from app import app
from models import db, PetitionResolution, PublicPetition, User, CorruptionReport, CorruptionResolution
from faker import Faker
from random import randint, choice as rc

if __name__ == "__main__":
    with app.app_context():

        fake = Faker()

        
        PetitionResolution.query.delete()
        PublicPetition.query.delete()
        CorruptionResolution.query.delete()
        CorruptionReport.query.delete()
        User.query.delete()

        users = []
        roles=["user", "admin"]

        users.append(User(
            fullname=fake.name(),
            email=fake.email(),
            password=fake.word(),
            id_passport_no=fake.random_number(),
            role=rc(roles)
        ))
        users.append(User(
            fullname=fake.name(),
            email=fake.email(),
            password=fake.word(),
            id_passport_no=fake.random_number(),
            role=rc(roles)
        ))

        db.session.add_all(users)
        db.session.commit()

        user_ids = [user.id for user in User.query.all()]
        print(user_ids)

        petitions = []

        ministries = ["Ministry of Interior and National Administration", 
                    "Ministry of Defense", 
                    "The National Treasury and Economic Planning",
                    "Ministry of Foreign and Diaspora Affairs",
                    "Ministry of Transport and Roads",
                    "Ministry of Public Service, Gender and Affirmative Action",
                    "Ministry of Health",
                    "Ministry of Education"
                    ]
        statuses=["Resolved", "Inprogress", "Rejected"]

        petitions.append(PublicPetition(
            govt_agency=rc(ministries),
            county=fake.country(),
            location_url=fake.url(),
            title=fake.sentence(nb_words=4),
            description=fake.sentence(nb_words=15),
            status=rc(statuses),
            user_id=rc(user_ids),
            latitude=fake.pyfloat(),
            longitude=fake.pyfloat()
        ))
        petitions.append(PublicPetition(
            govt_agency=rc(ministries),
            county=fake.country(),
            location_url=fake.url(),
            title=fake.sentence(nb_words=4),
            description=fake.sentence(nb_words=15),
            status=rc(statuses),
            user_id=rc(user_ids),
            latitude=fake.pyfloat(),
            longitude=fake.pyfloat()
        ))
        db.session.add_all(petitions)

        corruptions = []

        corruptions.append(CorruptionReport(
            govt_agency=rc(ministries),
            county=fake.country(),
            location_url=fake.url(),
            title=fake.sentence(nb_words=4),
            description=fake.sentence(nb_words=15),
            status=rc(statuses),
            user_id=rc(user_ids)
        ))
        corruptions.append(CorruptionReport(
            govt_agency=rc(ministries),
            county=fake.country(),
            location_url=fake.url(),
            title=fake.sentence(nb_words=4),
            description=fake.sentence(nb_words=15),
            status=rc(statuses),
            user_id=rc(user_ids)
        ))
        db.session.add_all(corruptions)


        p_resolutions = []
        p_record_ids = [petition.id for petition in PublicPetition.query.all()]

        p_resolutions.append(PetitionResolution(
            status=rc(statuses),
            justification=fake.sentence(nb_words=10),
            additional_comments=fake.paragraph(nb_sentences=3),
            record_id=rc(p_record_ids)
        ))
        p_resolutions.append(PetitionResolution(
            status=rc(statuses),
            justification=fake.sentence(nb_words=10),
            additional_comments=fake.paragraph(nb_sentences=3),
            record_id=rc(p_record_ids)
        ))
        db.session.add_all(p_resolutions)


        c_resolutions = []
        c_record_ids = [corruption.id for corruption in CorruptionReport.query.all()]

        c_resolutions.append(CorruptionResolution(
            status=rc(statuses),
            justification=fake.sentence(nb_words=10),
            additional_comments=fake.paragraph(nb_sentences=3),
            record_id=rc(c_record_ids)
        ))
        c_resolutions.append(CorruptionResolution(
            status=rc(statuses),
            justification=fake.sentence(nb_words=10),
            additional_comments=fake.paragraph(nb_sentences=3),
            record_id=rc(c_record_ids)
        ))

        db.session.add_all(c_resolutions)
        db.session.commit()


    


