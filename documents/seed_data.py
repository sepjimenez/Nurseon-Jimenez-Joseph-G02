from datetime import date


DOCUMENT_ID = "doc_01"
CATEGORY_NAME = "Pro-Practice"
CATEGORY_SLUG = "pro-practice"
DOCUMENT_DEFAULTS = {
    "title": "Nursing Ethics and Ethical Principles",
    "read_time": "12 mins (estimated)",
    "description": "Understand the ethical principles that guide professional nursing practice and patient-centered care.",
    "publish_date": date(2026, 6, 29),
    "is_published": True,
}

CONTENT_SECTIONS = [
    (
        "paragraph",
        "Nursing ethics refers to the moral principles and standards that guide nurses in providing safe, compassionate, and professional care. Ethical nursing practice promotes patient dignity, autonomy, and advocacy while ensuring accountability and integrity in all healthcare interactions. Nurses frequently encounter ethical dilemmas that require careful analysis, clinical judgment, and adherence to professional codes of ethics.",
    ),
    (
        "paragraph",
        "Autonomy is the ethical principle that recognizes a patient's right to make informed decisions regarding their own healthcare. Nurses must respect patients' values, beliefs, and preferences, even when these choices differ from the healthcare provider's recommendations. Supporting informed consent and ensuring that patients receive complete and understandable information are essential responsibilities of the nurse.",
    ),
    (
        "paragraph",
        "Beneficence refers to the obligation to act in the best interest of the patient by promoting health, preventing harm, and maximizing benefits. Nurses demonstrate beneficence by providing evidence-based interventions, advocating for appropriate treatment, and ensuring patient comfort and safety. Every nursing action should aim to improve patient outcomes and overall well-being.",
    ),
    (
        "paragraph",
        "Nonmaleficence, commonly summarized as 'do no harm,' requires nurses to avoid causing unnecessary injury or suffering. This principle includes preventing medication errors, maintaining competence, following safety protocols, and recognizing situations that place patients at risk. Nurses must carefully weigh potential benefits and risks before implementing interventions.",
    ),
    (
        "paragraph",
        "Justice involves fairness and equality in the distribution of healthcare resources and treatment. Nurses must provide equitable care regardless of a patient's age, gender, socioeconomic status, ethnicity, or cultural background. Ethical nursing practice demands that all patients receive respectful and unbiased care.",
    ),
    (
        "paragraph",
        "Fidelity and veracity are essential professional values in nursing. Fidelity refers to keeping commitments and maintaining trust, whereas veracity emphasizes honesty and truthfulness in all patient interactions. Nurses who uphold these principles strengthen therapeutic relationships and promote ethical healthcare environments.",
    ),
]

SOURCES = [
    "American Nurses Association. (2025). Code of Ethics for Nurses with Interpretive Statements. ANA Publishing.",
    "Butts, J.B., & Rich, K.L. (2024). Nursing Ethics: Across the Curriculum and Into Practice (6th ed.). Jones & Bartlett Learning.",
    "Grace, P.J. (2024). Nursing Ethics and Professional Responsibility in Advanced Practice (4th ed.). Jones & Bartlett Learning.",
]


def seed_nursing_ethics_document(apps, using, author):
    Category = apps.get_model("documents", "Category")
    NursingDocument = apps.get_model("documents", "NursingDocument")
    DocumentSection = apps.get_model("documents", "DocumentSection")
    DocumentSource = apps.get_model("documents", "DocumentSource")

    category, _ = Category.objects.using(using).get_or_create(
        name=CATEGORY_NAME,
        defaults={"slug": CATEGORY_SLUG},
    )
    if not category.slug:
        category.slug = CATEGORY_SLUG
        category.save(using=using, update_fields=["slug"])

    document, created = NursingDocument.objects.using(using).get_or_create(
        doc_id=DOCUMENT_ID,
        defaults={
            **DOCUMENT_DEFAULTS,
            "category": category,
            "created_by": author,
        },
    )
    if not created:
        return document, False

    DocumentSection.objects.using(using).bulk_create(
        [
            DocumentSection(
                document=document,
                order=order,
                section_type=section_type,
                text=text,
            )
            for order, (section_type, text) in enumerate(CONTENT_SECTIONS)
        ]
    )
    DocumentSource.objects.using(using).bulk_create(
        [
            DocumentSource(document=document, order=order, text=text)
            for order, text in enumerate(SOURCES, start=1)
        ]
    )
    return document, True
