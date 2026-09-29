# =========================================
# AIRSENTINEL-AI ALERT ENGINE
# =========================================

def generate_alert(
    risk_score,
    risk_level,
    aqi,
    pm25,
    pm10,
    high_risk_nodes
):

    # No alert for low risk
    if risk_level == "LOW":

        return {
            "alert": False,
            "severity": "LOW",
            "title": "No Immediate Alert",
            "message": (
                "Current environmental indicators "
                "do not require an immediate alert."
            ),
            "action": (
                "Continue routine monitoring."
            )
        }


    # Moderate alert
    if risk_level == "MODERATE":

        return {
            "alert": True,
            "severity": "MODERATE",
            "title": "Environmental Risk Alert",
            "message": (
                f"Environmental risk score is "
                f"{risk_score}/100. "
                f"AQI is {aqi}, with PM2.5 at "
                f"{pm25} and PM10 at {pm10}."
            ),
            "action": (
                "Monitor the affected area and "
                "review high-risk sensor nodes."
            )
        }


    # High alert
    return {
        "alert": True,
        "severity": "HIGH",
        "title": "High Environmental Risk Alert",
        "message": (
            f"Risk score is {risk_score}/100. "
            f"Current AQI is {aqi}. "
            f"PM2.5 is {pm25} and PM10 is {pm10}. "
            f"{high_risk_nodes} federated sensor node(s) "
            f"are currently high risk."
        ),
        "action": (
            "Investigate the affected area, "
            "review citizen observations, and "
            "increase environmental monitoring."
        )
    }


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    result = generate_alert(
        risk_score=75,
        risk_level="HIGH",
        aqi=111,
        pm25=32.9,
        pm10=55.9,
        high_risk_nodes=1
    )

    print()
    print("AirSentinel-AI Alert Engine")
    print("===========================")
    print()

    print("Alert:", result["alert"])
    print("Severity:", result["severity"])
    print("Title:", result["title"])
    print("Message:", result["message"])
    print("Action:", result["action"])

    print()