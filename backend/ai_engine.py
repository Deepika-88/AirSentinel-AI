# =========================================
# AIRSENTINEL-AI RISK ENGINE
# =========================================

def calculate_risk(aqi, pm25, pm10, high_risk_nodes):
    """
    Prototype environmental risk scoring engine.

    Inputs:
        aqi              Current air quality index
        pm25             PM2.5 concentration
        pm10             PM10 concentration
        high_risk_nodes  Number of high-risk federated nodes

    Returns:
        risk score, risk level and explanation
    """

    score = 0
    factors = []

    # -------------------------------------
    # AQI
    # -------------------------------------

    if aqi > 150:
        score += 40
        factors.append("very high AQI")

    elif aqi > 100:
        score += 30
        factors.append("elevated AQI")

    elif aqi > 50:
        score += 20
        factors.append("moderate AQI")

    # -------------------------------------
    # PM2.5
    # -------------------------------------

    if pm25 > 35:
        score += 25
        factors.append("elevated PM2.5")

    elif pm25 > 25:
        score += 15
        factors.append("moderate PM2.5")

    # -------------------------------------
    # PM10
    # -------------------------------------

    if pm10 > 50:
        score += 20
        factors.append("elevated PM10")

    elif pm10 > 40:
        score += 10
        factors.append("moderate PM10")

    # -------------------------------------
    # FEDERATED SENSOR NETWORK
    # -------------------------------------

    if high_risk_nodes >= 2:

        score += 15

        factors.append(
            f"{high_risk_nodes} high-risk sensor nodes"
        )

    elif high_risk_nodes == 1:

        score += 10

        factors.append(
            "1 high-risk sensor node"
        )

    # -------------------------------------
    # LIMIT SCORE
    # -------------------------------------

    score = min(score, 100)

    # -------------------------------------
    # RISK LEVEL
    # -------------------------------------

    if score >= 70:

        risk_level = "HIGH"

    elif score >= 40:

        risk_level = "MODERATE"

    else:

        risk_level = "LOW"

    # -------------------------------------
    # EXPLANATION
    # -------------------------------------

    if factors:

        explanation = (
            "Risk assessment is influenced by "
            + ", ".join(factors)
            + "."
        )

    else:

        explanation = (
            "Current environmental indicators "
            "show relatively low risk."
        )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "factors": factors,
        "explanation": explanation
    }


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    result = calculate_risk(
        aqi=81,
        pm25=33.1,
        pm10=38.5,
        high_risk_nodes=1
    )

    print()
    print("AirSentinel-AI Risk Engine")
    print("==========================")
    print()

    print(
        "Risk Score:",
        result["risk_score"]
    )

    print(
        "Risk Level:",
        result["risk_level"]
    )

    print(
        "Explanation:",
        result["explanation"]
    )

    print()