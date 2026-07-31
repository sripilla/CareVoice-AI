patterns = [

    # =====================================================
    # SYMPTOMS
    # =====================================================

    {"label": "SYMPTOM", "pattern": [{"LEMMA": "cough"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "fever"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "cold"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "headache"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "vomit"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "diarrhea"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "breathlessness"}]},
    {"label": "SYMPTOM", "pattern": [{"LEMMA": "breath"}]},

    {
        "label": "SYMPTOM",
        "pattern": [
            {"LOWER": "body"},
            {"LOWER": "pain"},
        ],
    },

    {
        "label": "SYMPTOM",
        "pattern": [
            {"LOWER": "chest"},
            {"LOWER": "pain"},
        ],
    },

    {
        "label": "SYMPTOM",
        "pattern": [
            {"LOWER": "sore"},
            {"LOWER": "throat"},
        ],
    },

    # =====================================================
    # DISEASES
    # =====================================================

    {"label": "DISEASE", "pattern": [{"LOWER": "diabetes"}]},
    {"label": "DISEASE", "pattern": [{"LOWER": "hypertension"}]},
    {"label": "DISEASE", "pattern": [{"LOWER": "asthma"}]},

    {
        "label": "DISEASE",
        "pattern": [
            {"LOWER": "blood"},
            {"LOWER": "pressure"},
        ],
    },

    {
        "label": "DISEASE",
        "pattern": [
            {"LOWER": "high"},
            {"LOWER": "blood"},
            {"LOWER": "pressure"},
        ],
    },

    {
        "label": "DISEASE",
        "pattern": [
            {"LOWER": "high"},
            {"LOWER": "bp"},
        ],
    },

    # =====================================================
    # MEDICATIONS
    # =====================================================

    {"label": "MEDICATION", "pattern": [{"LOWER": "paracetamol"}]},
    {"label": "MEDICATION", "pattern": [{"LOWER": "metformin"}]},
    {"label": "MEDICATION", "pattern": [{"LOWER": "insulin"}]},
    {"label": "MEDICATION", "pattern": [{"LOWER": "aspirin"}]},
    {"label": "MEDICATION", "pattern": [{"LOWER": "ibuprofen"}]},
    {"label": "MEDICATION", "pattern": [{"LOWER": "amoxicillin"}]},

    {
        "label": "MEDICATION",
        "pattern": [
            {"LOWER": "blood"},
            {"LOWER": "pressure"},
            {"LOWER": "medicine"},
        ],
    },

    {
        "label": "MEDICATION",
        "pattern": [
            {"LOWER": "bp"},
            {"LOWER": "medicine"},
        ],
    },

    {
        "label": "MEDICATION",
        "pattern": [
            {"LOWER": "iron"},
            {"LOWER": "tablet"},
        ],
    },

    {
        "label": "MEDICATION",
        "pattern": [
            {"LOWER": "iron"},
            {"LOWER": "tablets"},
        ],
    },

    {
        "label": "MEDICATION",
        "pattern": [
            {"LOWER": "vitamin"},
            {"LOWER": "d"},
        ],
    },

    {
        "label": "MEDICATION",
        "pattern": [{"LEMMA": "medicine"}],
    },

    {
        "label": "MEDICATION",
        "pattern": [{"LEMMA": "medication"}],
    },

    {
        "label": "MEDICATION",
        "pattern": [{"LEMMA": "tablet"}],
    },

    {
        "label": "MEDICATION",
        "pattern": [{"LEMMA": "capsule"}],
    },

]