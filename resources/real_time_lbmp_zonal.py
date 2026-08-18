import logging
import datetime
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.real_time_lbmp_zonal import RealTimeLBMPZonalIngestion, RealTimeLBMPZonalQuery, RealTimeLBMPZonalValidation
from nyiso_api.scrape.real_time_lbmp_zonal import scrape_real_time_lbmp_zonal
from nyiso_api.models.real_time_lbmp_zonal import RealTimeLBMPZonalModel
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

class RealTimeLBMPZonal(Resource):
    def post(self):
        payload = request.get_json() or {}

        try:
            validated = (
                RealTimeLBMPZonalIngestion()
                .load(payload)
            )
        except ValidationError as error:
            return {"errors": error.messages}, 400 

        dates = get_date_range(
            validated["start"],
            validated["end"],
        )

        scrape_real_time_lbmp_zonal(dates)      

        return {"message": "Real-time zonal LBMP data ingested"}, 200

    def get(self):
        # GET filters come from URL query parameters
        query_params = request.args.to_dict()

        if request.args.getlist("ptid"):
            query_params["ptid"] = request.args.getlist("ptid")

        try:
            validated = RealTimeLBMPZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        start = validated['start']
        end = validated['end']

        query = db.session.query(RealTimeLBMPZonalModel).filter(
            RealTimeLBMPZonalModel.timestamp.between(
                start,
                end,
            )
        )

        if ptids := validated.get("ptid"):
            query = query.filter(RealTimeLBMPZonalModel.ptid.in_(ptids))
        
        results = query.order_by(
            RealTimeLBMPZonalModel.timestamp,
            RealTimeLBMPZonalModel.ptid,
        ).all()

        return jsonify(RealTimeLBMPZonalValidation(many=True).dump(results))
