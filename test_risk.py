from careinsight.extractor import MedicalExtractor
from careinsight.risk_assessor import RiskAssessor

text = """
My name is Lakshmi.
I am 65 years old.
I have had a cough for three days.
I also have a mild fever.
I take blood pressure medicine every day.
I take paracetamol.
I have diabetes.
"""

extractor = MedicalExtractor()
data = extractor.extract(text)

assessor = RiskAssessor()
risk = assessor.assess(data)

print("\n========== EXTRACTED ==========\n")

for key, value in data.items():
    print(f"{key}: {value}")

print("\n========== RISK ==========\n")

for key, value in risk.items():
    print(f"{key}: {value}")