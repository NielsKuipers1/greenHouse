from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse
import plant_sensor_fake as ps

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return render_template('index.html')

class PlantApi(Resource):
    def get(self, plant_id: int):
        """
        returns a dictionary of plant info
        """
        # this should be replaced with reading sensor data
        data = ps.get_plant_info(plant_id) 

        return {plant_id: data}

class AllPlants(Resource):
    def get(self):
        return {"plant1" : ps.get_plant_info(1), "plant2" : ps.get_plant_info(2), "plant3" : ps.get_plant_info(3)}

def run_app():
    api.add_resource(PlantApi, '/api/plant<int:plant_id>')
    api.add_resource(AllPlants, '/api/plants')
    app.run()