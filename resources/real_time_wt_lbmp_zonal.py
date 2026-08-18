import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.real_time_wt_lbmp_zonal import RealTimeWT_LBMPZonalQuery, RealTimeWT_LBMPZonalValidation
from nyiso_api.scrape.real_time_wt_lbmp_zonal import scrape_real_time_wt_lbmp_zonal
from nyiso_api.models.real_time_wt_lbmp_zonal import RealTimeWT_LBMPZonalModel
from nyiso_api.utils.get_date_range import get_date_range

class RealTimeWeightedLBMPZonal(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = RealTimeWT_LBMPZonalQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_real_time_wt_lbmp_zonal(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Weighted real-time zonal LBMP data ingested"}, 200

    def get(self):
        query_params = request.args.to_dict()
        query_params["ptid"] = request.args.getlist("ptid")
        try:
            validated = RealTimeWT_LBMPZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(RealTimeWT_LBMPZonalModel).filter(RealTimeWT_LBMPZonalModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(RealTimeWT_LBMPZonalModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            RealTimeWT_LBMPZonalModel.timestamp,
            RealTimeWT_LBMPZonalModel.ptid,
        ).all()

        # Serialize data
        json_data = RealTimeWT_LBMPZonalValidation(many=True).dump(results)

        return jsonify(json_data)
