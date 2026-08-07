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
from nyiso_api.utils.find_missing_dates import find_missing_dates

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
        # POST request body, not URL query parameters
        payload = request.get_json() or {}

        try:
            validated = RealTimeLBMPZonalIngestion().load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        missing_dates = find_missing_dates(
            validated["start"],
            validated["end"],
            RealTimeLBMPZonalModel,
        )

        if missing_dates:
            scrape_real_time_lbmp_zonal(missing_dates)

        return {
            "message": "Ingestion complete",
            "start": validated["start"].isoformat(),
            "end": validated["end"].isoformat(),
        }, 201

    def get(self):
        # GET filters come from URL query parameters
        query_params = request.args.to_dict()

        if request.args.getlist("ptid"):
            query_params["ptid"] = request.args.getlist("ptid")

        try:
            validated = RealTimeLBMPZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        query = db.session.query(RealTimeLBMPZonalModel).filter(
            RealTimeLBMPZonalModel.timestamp.between(
                validated["start"],
                validated["end"],
            )
        )

        if ptids := validated.get("ptid"):
            query = query.filter(RealTimeLBMPZonalModel.ptid.in_(ptids))

        results = query.order_by(
            RealTimeLBMPZonalModel.timestamp,
            RealTimeLBMPZonalModel.ptid,
        ).all()

        return jsonify(RealTimeLBMPZonalValidation(many=True).dump(results))
