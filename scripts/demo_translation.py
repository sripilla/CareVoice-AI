from translation.translator import Translator

translator = Translator()

text = """
నా పేరు లక్ష్మి.
నా వయసు 65 సంవత్సరాలు.
నాకు మూడు రోజులుగా దగ్గు ఉంది.
"""

translation = translator.translate(text, "te")

print("\nEnglish Translation:\n")
print(translation)