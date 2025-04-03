import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CourseRecommender:
    def __init__(self, courses_db):
        self.courses = pd.read_csv(courses_db)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._prepare_data()  # Initialize during creation
        
    def _prepare_data(self):
        """Prepares the TF-IDF matrix during initialization"""
        self.courses['features'] = self.courses['title'] + " " + self.courses['description']
        self.tfidf_matrix = self.vectorizer.fit_transform(self.courses['features'])
        
    def recommend(self, student_courses, top_n=5):
        """Generate recommendations based on student's course history"""
        try:
            # Prepare student features
            student_features = " ".join([c["name"] for c in student_courses])
            
            # Transform student features using the pre-fitted vectorizer
            student_vec = self.vectorizer.transform([student_features])
            
            # Calculate similarities
            sim_scores = cosine_similarity(student_vec, self.tfidf_matrix).flatten()
            self.courses['similarity'] = sim_scores
            
            # Filter out already taken courses
            taken_codes = [c["code"] for c in student_courses]
            recommendations = self.courses[~self.courses["code"].isin(taken_codes)]
            
            return recommendations.sort_values("similarity", ascending=False).head(top_n)
            
        except Exception as e:
            raise RuntimeError(f"Recommendation failed: {str(e)}")

# Test the recommender
if __name__ == "__main__":
    recommender = CourseRecommender("courses.csv")
    test_courses = [{"code": "CS101", "name": "Introduction to Programming"}]
    print("Test recommendations:", recommender.recommend(test_courses))