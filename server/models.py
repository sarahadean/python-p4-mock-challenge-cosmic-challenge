from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serializer_rule = ('-scientist_missions.scientist')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)

    planets = association_proxy('scientist_missions', 'planet')
    scientist_missions = db.relationship('Mission', back_populates='scientist')

    @validates('name','field_of_study')
    def validate_scientist(self, key, string):
        if key == 'name':
            name = Scientist.query.filter_by(name=string).first()
            if string and not name:
                return string
            else:
                raise ValueError('Scientist must have name and must be unique')
        elif key == 'field_of_study':
            if string:
                return string
            else:
                raise ValueError('Scientist must have field of study')
            

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_only = ('name', 'distance_from_earth', 'nearest_star', 'image')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)

    planet_missions = db.relationship('Mission', back_populates='planet')

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    serializer_rules = ('-scientist.scientist_missions', '-planet.planet_missions')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    scientist = db.relationship('Scientist', back_populates='scientist_missions')
    planet = db.relationship('Planet', back_populates='planet_missions')

    @validates('name', 'scientist', 'planet')
    def validates_mission(self, key, string):
        if key == 'name':
            if string:
                return string
        elif key == 'scientist':
            if string:
                return string
        elif key == 'planet':
            if string:
                return string
        else:
            raise ValueError('Mission must have name, scientist and planet')
        
    def validates_scientist(self, key, scientist):
        if key == 'scientist':
            mission = Mission.query.filter_by(scientist=scientist).first()
            if not mission:
                return scientist
            else:
              raise ValueError('Scientist cannot join the same mission twice')
                




# add any models you may need. 