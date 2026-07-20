"""Supported FHIR Implementation Guides for the Conformance Validator UI."""

# Curated dropdown IGs (aligned with gaurav-validation POPULAR_IGS + local Da Vinci set).
SUPPORTED_IG_PACKAGES: frozenset[str] = frozenset({
    # Existing core set
    "hl7.fhir.us.core",
    "hl7.fhir.us.davinci-crd",
    "hl7.fhir.us.davinci-dtr",
    "hl7.fhir.us.davinci-pas",
    # Additional US Realm
    "hl7.fhir.us.ccda",
    "hl7.fhir.us.qicore",
    "hl7.fhir.us.carin-bb",
    "hl7.fhir.us.bulkdata",
    "hl7.fhir.us.odh",
    "hl7.fhir.us.military-service",
    "hl7.fhir.us.vrdr",
    "hl7.fhir.us.mcode",
    "hl7.fhir.us.ecr",
    "hl7.fhir.us.pacio-adi",
    "hl7.fhir.us.pacio-cs",
    "hl7.fhir.us.pacio-fs",
    # Additional Da Vinci
    "hl7.fhir.us.davinci-pdex",
    "hl7.fhir.us.davinci-cdex",
    "hl7.fhir.us.davinci-pcde",
    "hl7.fhir.us.davinci-alerts",
    "hl7.fhir.us.davinci-drug-formulary",
    "hl7.fhir.us.davinci-deqm",
    "hl7.fhir.us.davinci-ra",
    # UV base dependencies (selectable)
    "hl7.fhir.uv.ipa",
    "hl7.fhir.uv.ips",
    "hl7.fhir.uv.smart-app-launch",
    "hl7.fhir.uv.sdc",
    "hl7.fhir.uv.extensions.r4",
})

# Preferred on-disk versions when multiple .tgz exist for the same package id.
IG_PREFERRED_VERSIONS: dict[str, str] = {
    "hl7.fhir.us.core": "9.0.0",
    "hl7.fhir.us.ccda": "2.0.0",
    "hl7.fhir.us.qicore": "7.0.2",
    "hl7.fhir.us.carin-bb": "2.1.0",
    "hl7.fhir.us.bulkdata": "0.1.0",
    "hl7.fhir.us.odh": "1.3.0",
    "hl7.fhir.us.military-service": "1.0.0",
    "hl7.fhir.us.vrdr": "3.0.0",
    "hl7.fhir.us.davinci-crd": "2.2.1",
    "hl7.fhir.us.davinci-dtr": "2.2.0",
    "hl7.fhir.us.davinci-pas": "2.2.1",
    "hl7.fhir.us.davinci-pdex": "2.1.0",
    "hl7.fhir.us.davinci-cdex": "2.1.0",
    "hl7.fhir.us.davinci-hrex": "1.2.0",
    "hl7.fhir.us.davinci-pcde": "1.0.0",
    "hl7.fhir.us.davinci-alerts": "1.1.0",
    "hl7.fhir.us.davinci-drug-formulary": "2.1.0",
    "hl7.fhir.us.davinci-deqm": "5.0.0",
    "hl7.fhir.us.davinci-ra": "2.1.0",
    "hl7.fhir.us.mcode": "4.0.0",
    "hl7.fhir.us.ecr": "2.1.2",
    "hl7.fhir.us.pacio-adi": "1.0.0",
    "hl7.fhir.us.pacio-cs": "1.0.0",
    "hl7.fhir.us.pacio-fs": "1.0.0",
    "hl7.fhir.uv.ipa": "1.1.0",
    "hl7.fhir.uv.ips": "2.0.1",
    "hl7.fhir.uv.smart-app-launch": "2.2.0",
    "hl7.fhir.uv.sdc": "4.0.0",
    "hl7.fhir.uv.extensions.r4": "5.3.0",
}

# Display metadata for the dropdown (optional enrichment).
IG_DISPLAY: dict[str, dict[str, str]] = {
    "hl7.fhir.us.core": {"title": "US Core", "category": "HL7 US Realm"},
    "hl7.fhir.us.ccda": {"title": "C-CDA on FHIR", "category": "HL7 US Realm"},
    "hl7.fhir.us.qicore": {"title": "QI-Core", "category": "HL7 US Realm"},
    "hl7.fhir.us.carin-bb": {"title": "CARIN Blue Button", "category": "HL7 US Realm"},
    "hl7.fhir.us.bulkdata": {"title": "Bulk Data Access", "category": "HL7 US Realm"},
    "hl7.fhir.us.odh": {"title": "Occupational Data for Health", "category": "HL7 US Realm"},
    "hl7.fhir.us.military-service": {"title": "Military Service", "category": "HL7 US Realm"},
    "hl7.fhir.us.vrdr": {"title": "Vital Records Death Reporting", "category": "HL7 US Realm"},
    "hl7.fhir.us.mcode": {"title": "mCODE", "category": "HL7 US Realm"},
    "hl7.fhir.us.ecr": {"title": "eCR", "category": "HL7 US Realm"},
    "hl7.fhir.us.pacio-adi": {"title": "PACIO ADI", "category": "HL7 US Realm"},
    "hl7.fhir.us.pacio-cs": {"title": "PACIO Cognitive Status", "category": "HL7 US Realm"},
    "hl7.fhir.us.pacio-fs": {"title": "PACIO Functional Status", "category": "HL7 US Realm"},
    "hl7.fhir.us.davinci-crd": {"title": "Da Vinci CRD", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-dtr": {"title": "Da Vinci DTR", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-pas": {"title": "Da Vinci PAS", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-pdex": {"title": "Da Vinci PDex", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-cdex": {"title": "Da Vinci CDex", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-pcde": {"title": "Da Vinci PCDE", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-alerts": {"title": "Da Vinci Alerts", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-drug-formulary": {"title": "Da Vinci Drug Formulary", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-deqm": {"title": "Da Vinci DEQM", "category": "Da Vinci"},
    "hl7.fhir.us.davinci-ra": {"title": "Da Vinci Risk Adjustment", "category": "Da Vinci"},
    "hl7.fhir.uv.ipa": {"title": "International Patient Access", "category": "Base Dependencies"},
    "hl7.fhir.uv.ips": {"title": "International Patient Summary", "category": "Base Dependencies"},
    "hl7.fhir.uv.smart-app-launch": {"title": "SMART App Launch", "category": "Base Dependencies"},
    "hl7.fhir.uv.sdc": {"title": "Structured Data Capture (SDC)", "category": "Base Dependencies"},
    "hl7.fhir.uv.extensions.r4": {"title": "FHIR Extensions Pack", "category": "Base Dependencies"},
}

# Loaded as dependency when related Da Vinci IGs are selected (not shown in dropdown).
HIDDEN_IG_DEPENDENCIES: frozenset[str] = frozenset({
    "hl7.fhir.us.davinci-hrex",
})

# Additional packages for Upload-your-IG workflows (still on disk).
UPLOADABLE_EXTRA_IG_PACKAGES: frozenset[str] = frozenset({
    "hl7.terminology.r4",
})

# Load order when resolving dependencies (dependencies before dependents).
IG_LOAD_ORDER: tuple[str, ...] = (
    "hl7.fhir.us.core",
    "hl7.fhir.uv.extensions.r4",
    "hl7.fhir.uv.sdc",
    "hl7.fhir.uv.ipa",
    "hl7.fhir.uv.ips",
    "hl7.fhir.us.davinci-hrex",
    "hl7.fhir.us.davinci-crd",
    "hl7.fhir.us.davinci-pas",
    "hl7.fhir.us.davinci-dtr",
    "hl7.fhir.us.davinci-pdex",
    "hl7.fhir.us.davinci-cdex",
    "hl7.fhir.us.qicore",
    "hl7.fhir.us.mcode",
    "hl7.fhir.us.carin-bb",
)

DEFAULT_IGS_CSV: str = (
    "hl7.fhir.us.core#9.0.0,"
    "hl7.fhir.us.davinci-crd#2.2.1,"
    "hl7.fhir.us.davinci-dtr#2.2.0,"
    "hl7.fhir.us.davinci-pas#2.2.1"
)
