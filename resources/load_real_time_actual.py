import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.load_real_time_actual import LoadRealTimeActualQuery, LoadRealTimeActualValidation
from nyiso_api.scrape.load_real_time_actual import scrape_load_real_time_actual
from nyiso_api.models.load_real_time_actual import LoadRealTimeActualModel
from nyiso_api.utils.get_date_range import get_date_range

class LoadRealTimeActual(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = LoadRealTimeActualQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_load_real_time_actual(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Real-time actual load data ingested"}, 200

    def get(self):
        query_params = request.args.to_dict()
        if request.args.getlist("ptid"):
            query_params["ptid"] = request.args.getlist("ptid")
        if request.args.getlist("name"):
            query_params["name"] = request.args.getlist("name")
        try:
            validated = LoadRealTimeActualQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadRealTimeActualModel).filter(LoadRealTimeActualModel.timestamp.between(start, end))

        if validated.get('name'):
            query = query.filter(LoadRealTimeActualModel.name.in_(validated['name']))

        if validated.get('ptid'):
            query = query.filter(LoadRealTimeActualModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            LoadRealTimeActualModel.timestamp,
            LoadRealTimeActualModel.name,
        ).all()
    
        # Serialize data
        json_data = LoadRealTimeActualValidation(many=True).dump(results)

        return jsonify(json_data)
