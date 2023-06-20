#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Planet, Scientist, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return make_response({"message":"Hello Scientist"}, 200)

class Scientists(Resource):
    def get(self):
        scientist_list = [scientist.to_dict(only=('id', 'name', 'field_of_study', 'avatar')) for scientist in Scientist.query.all()]
        return make_response(scientist_list, 200)
    
    def post(self):
        data = request.get_json()
        try: 
            new_scientist = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study'),
                avatar=data.get('avatar')
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(), 201)
        except:
            return {'error':'400:Validation error'}, 400

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        try: 
            selected_scientist = Scientist.query.filter_by(id=id).first()
            return make_response(selected_scientist.to_dict(only=('id','name', 'field_of_study', 'avatar', 'planets')))
        except:
            return {'error': '404 Scientist does not exist'}, 404
        
    def patch(self, id):
        selected_scientist = Scientist.query.filter_by(id=id).first()
        if not selected_scientist:
            return ({'error':'404: Scientist not found'}, 404)
        else:
            data = request.get_json()
            for attr in data:
                setattr(selected_scientist, attr, data.get(attr))
            db.session.add(selected_scientist)
            db.session.commit()
            return make_response(selected_scientist.to_dict(only=('id','name', 'field_of_study', 'avatar', 'planets')), 202)
            # except:
            #     return {'error':'400: Validation Error'}, 400
        
    def delete(self, id):
        selected_scientist = Scientist.query.filter_by(id=id).first()
        if not selected_scientist:
            return {'error':'404: Scientist not found'}
        db.session.delete(selected_scientist)
        db.session.commit()
        return {"message": "Successful deletion"}, 204
    
api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planet_list = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star', 'image')) for planet in Planet.query.all()]
        return make_response(planet_list, 200)
     
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        data = request.get_json()
        try: 
            new_mission = Mission(
                name=data.get('name'),
                scientist_id=data.get('scientist_id'),
                planet_id=data.get('planet_id')
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except:
            return {'error':"400: Validation error"}

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
