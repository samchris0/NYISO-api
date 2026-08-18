import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.load_bid_zonal import LoadBidZonalQuery, LoadBidZonalValidation
from nyiso_api.scrape.load_bid_zonal import scrape_load_bid_zonal
from nyiso_api.models.load_bid_zonal import LoadBidZonalModel
from nyiso_api.utils.get_date_range import get_date_range

class LoadBidZonal(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = LoadBidZonalQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_load_bid_zonal(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Zonal load-bid data ingested"}, 200

    def get(self):
        query_params = request.args.to_dict()
        query_params["ptid"] = request.args.getlist("ptid")
        try:
            validated = LoadBidZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadBidZonalModel).filter(LoadBidZonalModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(LoadBidZonalModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            LoadBidZonalModel.timestamp,
            LoadBidZonalModel.ptid,
        ).all()
    
        # Serialize data
        json_data = LoadBidZonalValidation(many=True).dump(results)

        return jsonify(json_data)
