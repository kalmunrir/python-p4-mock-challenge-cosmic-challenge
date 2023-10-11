#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        try:
            new_scientist = Scientist(
                name=request.get_json()['name'],
                field_of_study=request.get_json()['field_of_study']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_scientist)
        db.session.commit()

        return make_response(new_scientist.to_dict(only=('id', 'name', 'field_of_study')), 200)
api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return make_response(scientist.to_dict(), 200)
        return make_response({"error": "Scientist not found"}, 404)
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()

        if scientist:
            dtp = request.get_json()
            errors = []
            for attr in dtp:
                try:
                    setattr(scientist, attr, dtp[attr])
                except ValueError as e:
                    errors.append(e.__repr__())
            if len(errors) != 0:
                return make_response({"errors": errors}, 400)
            else:
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(only=('id', 'name', 'field_of_study')), 202)
        
        return make_response({"error": "Scientist not found"}, 404)
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:
                db.session.delete(scientist)
                db.session.commit()
                return make_response('', 204)
            except Exception:
                return make_response('', 400)
        else:
            return make_response({"error": "Scientist not found"}, 404)
api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in Planet.query.all()]
        return make_response(planets, 200)
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        try:
            new_mission = Mission(
                name=request.get_json()['name'],
                scientist_id=request.get_json()['scientist_id'],
                planet_id=request.get_json()['planet_id']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_mission)
        db.session.commit()

        return make_response(new_mission.to_dict(), 200)
api.add_resource(Missions, '/missions')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
