from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse
import plant_sensor_fake as ps

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return render_template('index.html')

class PlantApi(Resource):
    def get(self):
        return {"plant1" : ps.get_plant_info(1), "plant2" : ps.get_plant_info(2), "plant3" : ps.get_plant_info(3)}
    

class ViewPlants(Resource):
    def get(self):
        return 
    
def run_app():
    api.add_resource(PlantApi, '/api/plants')
    api.add_resource(PlantApi, 'api/camera')
    app.run(host="0.0.0.0")