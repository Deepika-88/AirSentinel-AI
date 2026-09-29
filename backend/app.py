from flask import Flask, jsonify, request, send_from_directory
import os
import requests
from datetime import datetime
from statistics import mean
from werkzeug.utils import secure_filename

from ai_engine import calculate_risk
from alert_engine import generate_alert


app = Flask(__name__)


# =========================================
# FOLDERS
# =========================================

BASE_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

FRONTEND_FOLDER = os.path.join(
    BASE_FOLDER,
    "frontend"
)

DATA_FOLDER = os.path.join(
    BASE_FOLDER,
    "data"
)

UPLOAD_FOLDER = os.path.join(
    DATA_FOLDER,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


# =========================================
# CITIZEN OBSERVATIONS
# =========================================

observations = []


# =========================================
# FEDERATED SENSOR NODES
# =========================================

sensor_nodes = {
    "Hyderabad": {
        "pm25": 33.1,
        "pm10": 38.5,
        "no2": 35.0,
        "local_aqi": 81
    },
    "Mumbai": {
        "pm25": 42.5,
        "pm10": 55.2,
        "no2": 48.0,
        "local_aqi": 108
    },
    "Bengaluru": {
        "pm25": 21.8,
        "pm10": 30.4,
        "no2": 25.5,
        "local_aqi": 62
    }
}


# =========================================
# FEDERATED PROCESSING
# =========================================

def process_local_node(city, values):

    if values["local_aqi"] > 100:
        local_risk = "High"

    elif values["local_aqi"] > 50:
        local_risk = "Moderate"

    else:
        local_risk = "Low"

    return {
        "city": city,
        "local_aqi": values["local_aqi"],
        "risk": local_risk
    }


def federated_aggregate():

    local_results = []

    for city, values in sensor_nodes.items():

        result = process_local_node(
            city,
            values
        )

        local_results.append(result)

    average_aqi = mean(
        item["local_aqi"]
        for item in local_results
    )

    high_risk_nodes = sum(
        1
        for item in local_results
        if item["risk"] == "High"
    )

    return {
        "nodes": local_results,
        "aggregated_aqi": round(
            average_aqi,
            1
        ),
        "high_risk_nodes": high_risk_nodes,
        "raw_sensor_values_shared": False
    }


# =========================================
# OPEN DASHBOARD
# =========================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


# =========================================
# AIR QUALITY API
# =========================================

def get_air_quality():

    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        "?latitude=17.3850"
        "&longitude=78.4867"
        "&current=us_aqi,pm2_5,pm10,"
        "nitrogen_dioxide,sulphur_dioxide,ozone"
        "&hourly=us_aqi,pm2_5,pm10"
        "&forecast_hours=13"
        "&timezone=Asia%2FKolkata"
    )

    response = requests.get(
        url,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================
# DASHBOARD API
# =========================================

@app.route("/api/dashboard")
def dashboard():

    try:

        air_data = get_air_quality()

        current = air_data.get(
            "current",
            {}
        )

        hourly = air_data.get(
            "hourly",
            {}
        )

        hourly_aqi = hourly.get(
            "us_aqi",
            []
        )

        aqi = current.get(
            "us_aqi",
            0
        )

        if len(hourly_aqi) > 0:
            forecast_now = round(
                hourly_aqi[0]
            )
        else:
            forecast_now = round(aqi)

        if len(hourly_aqi) > 3:
            forecast_3 = round(
                hourly_aqi[3]
            )
        else:
            forecast_3 = forecast_now

        if len(hourly_aqi) > 6:
            forecast_6 = round(
                hourly_aqi[6]
            )
        else:
            forecast_6 = forecast_3

        if len(hourly_aqi) > 12:
            forecast_12 = round(
                hourly_aqi[12]
            )
        else:
            forecast_12 = forecast_6

        if aqi <= 50:
            risk = "Good"

        elif aqi <= 100:
            risk = "Moderate"

        elif aqi <= 150:
            risk = "Unhealthy for Sensitive Groups"

        elif aqi <= 200:
            risk = "Unhealthy"

        elif aqi <= 300:
            risk = "Very Unhealthy"

        else:
            risk = "Hazardous"

        if forecast_now > 0:

            percentage_change = (
                (
                    forecast_12 - forecast_now
                )
                / forecast_now
            ) * 100

        else:

            percentage_change = 0

        return jsonify({

            "success": True,

            "aqi": round(aqi),

            "hotspots": 7,

            "risk": risk,

            "prediction": (
                f"{percentage_change:+.1f}%"
            ),

            "forecast": {

                "now": forecast_now,

                "3_hours": forecast_3,

                "6_hours": forecast_6,

                "12_hours": forecast_12

            },

            "pollutants": {

                "pm2_5":
                    current.get("pm2_5"),

                "pm10":
                    current.get("pm10"),

                "nitrogen_dioxide":
                    current.get(
                        "nitrogen_dioxide"
                    ),

                "sulphur_dioxide":
                    current.get(
                        "sulphur_dioxide"
                    ),

                "ozone":
                    current.get("ozone")

            },

            "source":
                "Open-Meteo Air Quality API"

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Air quality data unavailable",

            "error":
                str(error)

        }), 500


# =========================================
# FEDERATED API
# =========================================

@app.route("/api/federated")
def federated():

    try:

        result = federated_aggregate()

        return jsonify({

            "success": True,

            **result

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Federated network unavailable",

            "error":
                str(error)

        }), 500


# =========================================
# AI RISK ANALYSIS API
# =========================================

@app.route("/api/ai-analysis")
def ai_analysis():

    try:

        air_data = get_air_quality()

        current = air_data.get(
            "current",
            {}
        )

        aqi = current.get(
            "us_aqi",
            0
        )

        pm25 = current.get(
            "pm2_5",
            0
        )

        pm10 = current.get(
            "pm10",
            0
        )

        federated_data = federated_aggregate()

        high_risk_nodes = federated_data[
            "high_risk_nodes"
        ]

        result = calculate_risk(

            aqi=aqi,

            pm25=pm25,

            pm10=pm10,

            high_risk_nodes=
                high_risk_nodes

        )

        return jsonify({

            "success": True,

            "risk_score":
                result["risk_score"],

            "risk_level":
                result["risk_level"],

            "factors":
                result["factors"],

            "explanation":
                result["explanation"],

            "inputs": {

                "aqi":
                    aqi,

                "pm25":
                    pm25,

                "pm10":
                    pm10,

                "high_risk_nodes":
                    high_risk_nodes

            }

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "AI risk analysis unavailable",

            "error":
                str(error)

        }), 500


# =========================================
# ALERT API
# =========================================

@app.route("/api/alert")
def alert():

    try:

        air_data = get_air_quality()

        current = air_data.get(
            "current",
            {}
        )

        aqi = current.get(
            "us_aqi",
            0
        )

        pm25 = current.get(
            "pm2_5",
            0
        )

        pm10 = current.get(
            "pm10",
            0
        )

        federated_data = federated_aggregate()

        high_risk_nodes = federated_data[
            "high_risk_nodes"
        ]

        risk_result = calculate_risk(

            aqi=aqi,

            pm25=pm25,

            pm10=pm10,

            high_risk_nodes=
                high_risk_nodes

        )

        alert_result = generate_alert(

            risk_score=
                risk_result["risk_score"],

            risk_level=
                risk_result["risk_level"],

            aqi=
                aqi,

            pm25=
                pm25,

            pm10=
                pm10,

            high_risk_nodes=
                high_risk_nodes

        )

        return jsonify({

            "success": True,

            **alert_result,

            "risk_score":
                risk_result["risk_score"],

            "inputs": {

                "aqi":
                    aqi,

                "pm25":
                    pm25,

                "pm10":
                    pm10,

                "high_risk_nodes":
                    high_risk_nodes

            }

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Alert engine unavailable",

            "error":
                str(error)

        }), 500


# =========================================
# WEATHER API
# =========================================

@app.route("/api/weather")
def weather():

    try:

        url = (

            "https://api.open-meteo.com/v1/forecast"

            "?latitude=17.3850"

            "&longitude=78.4867"

            "&current=temperature_2m,"

            "relative_humidity_2m,"

            "wind_speed_10m,"

            "precipitation"

        )

        response = requests.get(

            url,

            timeout=10

        )

        response.raise_for_status()

        weather_data = response.json()

        current = weather_data[
            "current"
        ]

        return jsonify({

            "success": True,

            "location":
                "Hyderabad",

            "temperature":
                current.get(
                    "temperature_2m"
                ),

            "humidity":
                current.get(
                    "relative_humidity_2m"
                ),

            "wind_speed":
                current.get(
                    "wind_speed_10m"
                ),

            "precipitation":
                current.get(
                    "precipitation"
                ),

            "time":
                current.get(
                    "time"
                )

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Weather data unavailable",

            "error":
                str(error)

        }), 500


# =========================================
# FILE VALIDATION
# =========================================

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS

    )


# =========================================
# SERVE UPLOADED PHOTOS
# =========================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(filename):

    return send_from_directory(

        UPLOAD_FOLDER,

        filename

    )


# =========================================
# CITIZEN OBSERVATION API
# =========================================

@app.route(
    "/api/observation",
    methods=["POST"]
)
def add_observation():

    location = request.form.get(
        "location",
        "Unknown"
    )

    latitude = request.form.get(
        "latitude"
    )

    longitude = request.form.get(
        "longitude"
    )

    pollution_type = request.form.get(
        "pollution_type",
        "Unknown"
    )

    severity = request.form.get(
        "severity",
        "Unknown"
    )

    description = request.form.get(
        "description",
        ""
    )

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        latitude = None

        longitude = None

    photo_url = None

    if "photo" in request.files:

        photo = request.files["photo"]

        if photo and photo.filename:

            if not allowed_file(
                photo.filename
            ):

                return jsonify({

                    "success": False,

                    "message":
                        "Unsupported image format"

                }), 400

            filename = secure_filename(
                photo.filename
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            filename = (
                timestamp
                + "_"
                + filename
            )

            photo_path = os.path.join(

                UPLOAD_FOLDER,

                filename

            )

            photo.save(
                photo_path
            )

            photo_url = (
                "/uploads/"
                + filename
            )

    observation = {

        "id":
            len(observations) + 1,

        "location":
            location,

        "latitude":
            latitude,

        "longitude":
            longitude,

        "pollution_type":
            pollution_type,

        "severity":
            severity,

        "description":
            description,

        "photo_url":
            photo_url,

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    }

    observations.append(
        observation
    )

    return jsonify({

        "success": True,

        "message":
            "Citizen observation submitted successfully",

        "observation":
            observation

    })


# =========================================
# GET CITIZEN OBSERVATIONS
# =========================================

@app.route(
    "/api/observations"
)
def get_observations():

    return jsonify({

        "count":
            len(observations),

        "observations":
            observations

    })


# =========================================
# START SERVER
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )