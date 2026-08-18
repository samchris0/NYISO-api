import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.real_time_lbmp_generator import RealTimeLBMPGeneratorQuery, RealTimeLBMPGeneratorValidation
from nyiso_api.scrape.real_time_lbmp_generator import scrape_real_time_lbmp_generator
from nyiso_api.models.real_time_lbmp_generator import RealTimeLBMPGeneratorModel
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

class RealTimeLBMPGenerator(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = RealTimeLBMPGeneratorQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_real_time_lbmp_generator(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Real-time generator LBMP data ingested"}, 200

    def get(self):
        query_params = request.args.to_dict()
        query_params["ptid"] = request.args.getlist("ptid")
        try:
            validated = RealTimeLBMPGeneratorQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(RealTimeLBMPGeneratorModel).filter(RealTimeLBMPGeneratorModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(RealTimeLBMPGeneratorModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            RealTimeLBMPGeneratorModel.timestamp,
            RealTimeLBMPGeneratorModel.ptid,
        ).all()

        # Serialize data
        json_data = RealTimeLBMPGeneratorValidation(many=True).dump(results)

        return jsonify(json_data)
