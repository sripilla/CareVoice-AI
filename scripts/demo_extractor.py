from careinsight.extractor import MedicalExtractor

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

result = extractor.extract(text)

print("\n========== EXTRACTED DATA ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")