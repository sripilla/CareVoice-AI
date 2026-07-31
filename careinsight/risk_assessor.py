class RiskAssessor:

    def assess(self, data):

        score = 0

        # -------- Age --------
        if data["age"] and data["age"] >= 60:
            score += 1

        # -------- Symptoms --------
        if "fever" in data["symptoms"]:
            score += 1

        if "cough" in data["symptoms"]:
            score += 1

        if "breathlessness" in data["symptoms"]:
            score += 2

        # -------- Conditions --------
        if "Diabetes" in data["conditions"]:
            score += 1

        if "Hypertension" in data["conditions"]:
            score += 1

        # -------- Risk Level --------
        if score <= 1:
            level = "Low"

        elif score <= 3:
            level = "Medium"

        else:
            level = "High"

        return {
            "risk_score": score,
            "risk_level": level,
        }