"""Unit tests for profile URL to package mapping."""

from app.utils.fhir_helpers import profile_url_to_package_id


def test_profile_url_to_package_id_us_core():
    url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    assert profile_url_to_package_id(url) == "hl7.fhir.us.core"


def test_profile_url_to_package_id_davinci_pas():
    url = "http://hl7.org/fhir/us/davinci-pas/StructureDefinition/pas-claim"
    assert profile_url_to_package_id(url) == "hl7.fhir.us.davinci-pas"


def test_profile_url_to_package_id_uv_smart():
    url = "http://hl7.org/fhir/uv/smart-app-launch/StructureDefinition/smart-app-launch"
    assert profile_url_to_package_id(url) == "hl7.fhir.uv.smart-app-launch"


def test_profile_url_to_package_id_invalid():
    assert profile_url_to_package_id("http://example.org/Profile/foo") is None
