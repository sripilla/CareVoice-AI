from careinsight.summarizer import MedicalSummarizer

text = """
My name is Lakshmi.
I am 65 years old.
I have had a cough for three days.
I also have a mild fever.
I take blood pressure medicine every day.
I take paracetamol.
I have diabetes.
"""

summarizer = MedicalSummarizer()

summary = summarizer.summarize_text(text)

print("\n========== SUMMARY ==========\n")

print(summary)