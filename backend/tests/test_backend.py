"""Tests for transcript parsing, recommendations and the upload endpoint."""

import io
import sys
from pathlib import Path

BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from recommender import CourseRecommender  # noqa: E402
from transcript_parser import parse_courses  # noqa: E402

SAMPLE = BACKEND.parent / "samples" / "sample_transcript.txt"


# --- parsing ---------------------------------------------------------------

def test_parses_code_and_title_and_ignores_grades():
    courses = parse_courses("CS101    Introduction to Programming    15    A")

    assert courses == [{"code": "CS101", "title": "Introduction to Programming"}]


def test_code_with_space_is_normalised():
    courses = parse_courses("ECMM 422 Machine Learning 90")

    assert courses[0]["code"] == "ECMM422"


def test_headers_and_prose_are_ignored():
    text = "Academic Transcript\nCode Module Credits Grade\nOverall average: 68.5"

    assert parse_courses(text) == []


def test_sample_transcript_has_six_courses():
    courses = parse_courses(SAMPLE.read_text())

    assert [c["code"] for c in courses] == ["CS101", "CS201", "CS220", "SEC201", "DS201", "MATH101"]


# --- recommending ----------------------------------------------------------

recommender = CourseRecommender(BACKEND / "catalogue.csv")


def test_taken_courses_are_never_recommended():
    taken = [{"code": "CS101", "title": "Introduction to Programming"}]
    codes = set(recommender.recommend(taken, top_n=50)["code"])

    assert "CS101" not in codes


def test_security_history_leads_to_security_courses():
    taken = [
        {"code": "CS101", "title": "Introduction to Programming"},
        {"code": "CS220", "title": "Computer Networks"},
        {"code": "SEC201", "title": "Introduction to Cyber Security"},
    ]
    top = list(recommender.recommend(taken, top_n=3)["code"])

    assert sum(code.startswith("SEC") for code in top) >= 2


def test_data_history_leads_to_data_courses():
    taken = [
        {"code": "CS101", "title": "Introduction to Programming"},
        {"code": "DS201", "title": "Introduction to Data Science"},
        {"code": "MATH210", "title": "Probability and Statistics"},
    ]
    top = list(recommender.recommend(taken, top_n=3)["code"])

    assert sum(code.startswith(("DS", "MATH")) for code in top) >= 2


def test_prerequisites_are_checked():
    taken = [{"code": "SEC201", "title": "Introduction to Cyber Security"}]
    ranked = recommender.recommend(taken, top_n=50).set_index("code")

    assert ranked.loc["SEC302", "prereqs_met"]          # needs SEC201: passed
    assert not ranked.loc["SEC301", "prereqs_met"]      # also needs CS220: missing


def test_unknown_course_titles_still_work():
    taken = [{"code": "XYZ999", "title": "Cryptography and Network Defence"}]
    top = recommender.recommend(taken, top_n=3)

    assert top["match"].iloc[0] > 0


# --- API -------------------------------------------------------------------

client = app.test_client()


def upload(data: bytes, name: str):
    return client.post("/api/recommend", data={"file": (io.BytesIO(data), name)},
                       content_type="multipart/form-data")


def test_api_returns_recommendations_and_charts():
    response = upload(SAMPLE.read_bytes(), "transcript.txt")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["courses_found"]) == 6
    assert len(body["recommendations"]) == 5
    assert set(body["visualizations"]) == {"pie", "bar", "radar"}


def test_api_rejects_other_file_types():
    response = upload(b"MZ fake", "transcript.exe")

    assert response.status_code == 400


def test_api_explains_when_no_courses_found():
    response = upload(b"just some text", "notes.txt")

    assert response.status_code == 422


def test_each_recommendation_says_why():
    taken = [{"code": "SEC201", "title": "Introduction to Cyber Security"},
             {"code": "DS201", "title": "Introduction to Data Science"}]
    top = recommender.recommend(taken, top_n=5).set_index("code")

    assert top.loc["SEC320", "because_of"] == "Introduction to Cyber Security"
