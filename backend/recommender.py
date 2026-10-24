"""Content-based course recommender using TF-IDF and cosine similarity.

Every catalogue course becomes a TF-IDF vector built from its title, subject
area, description and skills. Each course the student has taken becomes a
vector too (from its catalogue entry if it is in the catalogue, otherwise from
its title). A candidate course scores as the cosine similarity to the taken
course it is closest to, so every recommendation can be explained: "suggested
because you took X".
"""

from typing import Dict, List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Subject-area words are repeated so that courses in the same area count as
# similar even when their descriptions share few words, and so that a word
# like "networks" in "Computer Networks" does not pull in "Neural Networks".
AREA_WEIGHT = 3


class CourseRecommender:
    def __init__(self, catalogue_csv):
        self.courses = pd.read_csv(catalogue_csv, keep_default_na=False)
        self.courses["features"] = (
            self.courses["title"] + " " + (self.courses["area"] + " ") * AREA_WEIGHT + self.courses["description"]
            + " " + self.courses["skills"].str.replace(";", " ")
        )
        self.vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(self.courses["features"])
        self._features_by_code = self.courses.set_index("code")["features"].to_dict()

    def recommend(self, taken: List[Dict[str, str]], top_n: int = 5) -> pd.DataFrame:
        """Rank untaken catalogue courses by similarity to the student's history.

        Adds three columns:
          match        cosine similarity (0-100) to the closest taken course
          because_of   the title of that closest taken course
          prereqs_met  whether every prerequisite has already been passed
        """
        if not taken:
            raise ValueError("No courses found in the transcript")

        taken_text = [self._features_by_code.get(c["code"], c["title"]) for c in taken]
        similarity = cosine_similarity(self.vectorizer.transform(taken_text), self.matrix)  # taken x catalogue
        closest = similarity.argmax(axis=0)
        taken_codes = {c["code"] for c in taken}

        result = self.courses.assign(
            match=(similarity.max(axis=0) * 100).round(1),
            because_of=[taken[i]["title"] for i in closest],
        )
        result = result[~result["code"].isin(taken_codes)].copy()
        result["prereqs_met"] = result["prerequisites"].apply(
            lambda p: all(code in taken_codes for code in p.split(";") if code)
        )
        return result.sort_values("match", ascending=False).head(top_n).drop(columns=["features"])
