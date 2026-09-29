from statistics import mean


# =========================================
# LOCAL SENSOR NODES
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
# LOCAL PROCESSING
# =========================================

def process_local_node(city, values):

    # Only calculated summaries are shared.
    local_risk = (
        "High"
        if values["local_aqi"] > 100
        else "Moderate"
        if values["local_aqi"] > 50
        else "Low"
    )

    return {

        "city": city,

        "local_aqi": values["local_aqi"],

        "risk": local_risk

    }


# =========================================
# FEDERATED AGGREGATION
# =========================================

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

        "aggregated_aqi":
            round(average_aqi, 1),

        "high_risk_nodes":
            high_risk_nodes,

        "raw_sensor_values_shared":
            False

    }


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    result = federated_aggregate()

    print("\nFederated Climate Network")
    print("=========================\n")

    for node in result["nodes"]:

        print(
            f'{node["city"]}: '
            f'AQI={node["local_aqi"]}, '
            f'Risk={node["risk"]}'
        )

    print(
        "\nAggregated AQI:",
        result["aggregated_aqi"]
    )

    print(
        "High-risk nodes:",
        result["high_risk_nodes"]
    )

    print(
        "Raw sensor values shared:",
        result["raw_sensor_values_shared"]
    )