import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.load_iso_forecast import LoadISOForecastQuery, LoadISOForecastValidation
from nyiso_api.scrape.load_iso_forecast import scrape_load_iso_forecast
from nyiso_api.models.load_iso_forecast import LoadISOForecastModel
from nyiso_api.utils.get_date_range import get_date_range

class LoadISOForecast(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = LoadISOForecastQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_load_iso_forecast(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "ISO load forecast data ingested"}, 200

    def get(self):
        query_params = request.args.to_dict()
        if request.args.getlist("name"):
            query_params["name"] = request.args.getlist("name")
        try:
            validated = LoadISOForecastQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadISOForecastModel).filter(LoadISOForecastModel.timestamp.between(start, end))

        if validated.get('name'):
            query = query.filter(LoadISOForecastModel.name.in_(validated['name']))

        results = query.order_by(
            LoadISOForecastModel.timestamp,
            LoadISOForecastModel.name,
        ).all()
    
        # Serialize data
        json_data = LoadISOForecastValidation(many=True).dump(results)

        return jsonify(json_data)
