from flask import Flask, render_template
from flask_restful import Api, Resource

import fake_humidity_sensor as ps

class WebApp:
    def __init__(self, main):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.m = main

        @self.app.route('/')
        def index():
            return render_template('index.html')

        class PlantApi(Resource):
            def get(self):
                return {"plant1" : ps.get_plant_info(1), "plant2" : ps.get_plant_info(2), "plant3" : ps.get_plant_info(3)}

        class ViewPlants(Resource):
            def __init__(self, main):
                self.m = main
            def get(self):
                self.m.tringger_camera()
                return 

        self.api.add_resource(PlantApi, '/api/plants')
        self.api.add_resource(ViewPlants, '/api/camera', resource_class_args=[self.m])

    def run(self):
        try:
            self.app.run(host="0.0.0.0")
        except KeyboardInterrupt:
            self.m.exit()    