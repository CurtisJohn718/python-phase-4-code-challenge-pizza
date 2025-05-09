#!/usr/bin/env python3
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants]
        return make_response(response, 200)
    

# GET /restaurants/<int:id>
class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(restaurant.to_dict(), 200)
        return make_response({"error": "Restaurant not found"}, 404)
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200
    

# POST /restaurant_pizzas
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            price = int(data["price"])
            pizza_id = int(data["pizza_id"])
            restaurant_id = int(data["restaurant_id"])
        except (KeyError, ValueError):
            return {"errors": ["validation errors"]}, 400
        
        if not(1 <= price <= 30):
            return {"errors": ["validation errors"]}, 400
        
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return {"errors": ["validation errors"]}, 400
        
        new_rp = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
        db.session.add(new_rp)
        db.session.commit()

        return new_rp.to_dict(), 201
    
# Register routes
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

# Run server
if __name__ == "__main__":
    app.run(port=5555, debug=True)
