from utilities.setup_server import app, db, migrate

#  association Tables
association_JobOffer_Location = db.Table('association_JobOffer_Location',
                                         db.Column('job_offer_id', db.ForeignKey('JobOffer.offer_url'),
                                                   primary_key=True),
                                         db.Column('location', db.ForeignKey('Location.location'), primary_key=True)
                                         )
association_JobOffer_Experience = db.Table('association_JobOffer_Experience',
                                           db.Column('job_offer_id', db.ForeignKey('JobOffer.offer_url'),
                                                     primary_key=True),
                                           db.Column('experience', db.ForeignKey('Experience.experience'),
                                                     primary_key=True)
                                           )
association_JobOffer_Employment_type = db.Table('association_JobOffer_Employment_type',
                                                db.Column('job_offer_id', db.ForeignKey('JobOffer.offer_url'),
                                                          primary_key=True),
                                                db.Column('employment_type',
                                                          db.ForeignKey('Employment_type.employment_type'),
                                                          primary_key=True)
                                                )
association_JobOffer_Skill_must = db.Table('association_JobOffer_Skill_must',
                                           db.Column('job_offer_id', db.ForeignKey('JobOffer.offer_url'),
                                                     primary_key=True),
                                           db.Column('skill', db.ForeignKey('Skill.skill'), primary_key=True)
                                           )
association_JobOffer_Skill_nice = db.Table('association_JobOffer_Skill_nice',
                                           db.Column('job_offer_id', db.ForeignKey('JobOffer.offer_url'),
                                                     primary_key=True),
                                           db.Column('skill', db.ForeignKey('Skill.skill'), primary_key=True)
                                           )


class ChildFinder:
    @classmethod
    def find_kid(cls, given_name):
        for kid in ChildFinder.__subclasses__():
            if kid.__name__ == given_name:
                return kid.__name__


#  main Tables
class JobOffer(db.Model, ChildFinder):
    __tablename__ = 'JobOffer'
    #  fields
    offer_url = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    b2b_min = db.Column(db.Integer)
    b2b_max = db.Column(db.Integer)
    permanent_min = db.Column(db.Integer)
    permanent_max = db.Column(db.Integer)
    mandate_min = db.Column(db.Integer)
    mandate_max = db.Column(db.Integer)
    expired = db.Column(db.String)
    expired_at = db.Column(db.String)
    scraped_at = db.Column(db.String)
    #  many to one
    company_name = db.Column(db.String, db.ForeignKey('Company.company'))
    from_jobsite = db.Column(db.String, db.ForeignKey('Jobsite.jobsite'))
    company = db.relationship("Company",
                              back_populates="company_to_job_offer")
    jobsite = db.relationship("Jobsite",
                              back_populates="jobsite_to_job_offer")
    #  many to many
    location = db.relationship("Location",
                               secondary=association_JobOffer_Location,
                               back_populates='location_to_job_offer')
    experience = db.relationship("Experience",
                                 secondary=association_JobOffer_Experience,
                                 back_populates='experience_to_job_offer')
    employment_type = db.relationship("Employment_type",
                                      secondary=association_JobOffer_Employment_type,
                                      back_populates='employment_type_to_job_offer')
    skill_must = db.relationship("Skill",
                                 secondary=association_JobOffer_Skill_must,
                                 back_populates='skill_must_to_job_offer')
    skill_nice = db.relationship("Skill",
                                 secondary=association_JobOffer_Skill_nice,
                                 back_populates='skill_nice_to_job_offer')


class Company(db.Model, ChildFinder):
    __tablename__ = 'Company'
    #  fields
    # id = db.Column(Integer, primary_key=True)
    # company_uuid = db.Column(db.String, primary_key=True)
    company = db.Column(db.String, primary_key=True)
    company_size = db.Column(db.String)
    #  one to many
    company_to_job_offer = db.relationship("JobOffer",
                                           back_populates='company')


class Jobsite(db.Model, ChildFinder):
    __tablename__ = 'Jobsite'
    #  fields
    # id = db.Column(Integer, primary_key=True)
    # jobsite_uuid = db.Column(db.String, primary_key=True)
    jobsite = db.Column(db.String, primary_key=True)
    #  one to many
    jobsite_to_job_offer = db.relationship("JobOffer",
                                           back_populates='jobsite')


class Location(db.Model, ChildFinder):
    __tablename__ = 'Location'
    #  fields
    # id = db.Column(Integer, primary_key=True)
    # location_uuid = db.Column(db.String, primary_key=True)
    location = db.Column(db.String, primary_key=True)
    #  many to many
    location_to_job_offer = db.relationship("JobOffer",
                                            secondary=association_JobOffer_Location,
                                            back_populates='location')


class Experience(db.Model, ChildFinder):
    __tablename__ = 'Experience'
    #  fields
    # id = db.Column(Integer, primary_key=True)
    # experience_uuid = db.Column(db.String, primary_key=True)
    experience = db.Column(db.String, primary_key=True)
    #  many to many
    experience_to_job_offer = db.relationship("JobOffer",
                                              secondary=association_JobOffer_Experience,
                                              back_populates='experience')


class Employment_type(db.Model, ChildFinder):
    __tablename__ = "Employment_type"
    #  fields
    # id = db.Column(Integer, primary_key=True)
    # employment_type_uuid = db.Column(db.String, primary_key=True)
    employment_type = db.Column(db.String, primary_key=True)
    #  many to many
    employment_type_to_job_offer = db.relationship("JobOffer",
                                                   secondary=association_JobOffer_Employment_type,
                                                   back_populates='employment_type')


class Skill(db.Model, ChildFinder):
    __tablename__ = "Skill"
    #  fields
    # id = db.Column(Integer, primary_key=True)
    # skill_uuid = db.Column(db.String, primary_key=True)
    skill = db.Column(db.String, primary_key=True)
    # many to many
    skill_must_to_job_offer = db.relationship("JobOffer",
                                              secondary=association_JobOffer_Skill_must,
                                              back_populates='skill_must')
    skill_nice_to_job_offer = db.relationship("JobOffer",
                                              secondary=association_JobOffer_Skill_nice,
                                              back_populates='skill_nice')
