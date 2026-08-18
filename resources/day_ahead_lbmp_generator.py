import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.day_ahead_lbmp_generator import DayAheadLBMPGeneratorQuery, DayAheadLBMPGeneratorValidation
from nyiso_api.scrape.day_ahead_lbmp_generator import scrape_day_ahead_lbmp_generator
from nyiso_api.models.day_ahead_lbmp_generator import DayAheadLBMPGeneratorModel
from nyiso_api.utils.get_date_range import get_date_range

"""
Variables returned:
timestamp
ptid
name
lbmp: The locational based marginal price for a given time and location
marginal_cost_losses: Extra energy (and cost) required to produce to counteract transmission loss
marginal_cost_congestion: Added cost due to transmission constraints
"""

logger = logging.getLogger(__name__)

class DayAheadLBMPGenerator(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = DayAheadLBMPGeneratorQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_day_ahead_lbmp_generator(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Day-ahead generator LBMP data ingested"}, 200

    def get(self):
        query_params = request.args.to_dict()
        query_params["ptid"] = request.args.getlist("ptid")
        try:
            validated = DayAheadLBMPGeneratorQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(DayAheadLBMPGeneratorModel).filter(DayAheadLBMPGeneratorModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(DayAheadLBMPGeneratorModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            DayAheadLBMPGeneratorModel.timestamp,
            DayAheadLBMPGeneratorModel.ptid,
        ).all()

        # Serialize data
        json_data = DayAheadLBMPGeneratorValidation(many=True).dump(results)

        return jsonify(json_data)
