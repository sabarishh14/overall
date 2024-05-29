import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def top_mentors_for_mentee(mentee_email, top_n=1):
    if not firebase_admin._apps:
        cred = credentials.Certificate("credentials.json") 
        firebase_admin.initialize_app(cred, {"databaseURL": "https://limble-30e8a-default-rtdb.asia-southeast1.firebasedatabase.app/"})

    ref = db.reference('/')

    mentors_data = ref.child('mentor').get()
    mentees_data = ref.child('mentee').get()

    menteedf = list(mentees_data.values())
    mentordf = list(mentors_data.values())

    mentors_df = pd.DataFrame(mentordf)
    mentees_df = pd.DataFrame(menteedf)

    mentors_df['mentor_profile'] = mentors_df['designation'] + ' ' + mentors_df['field_of_work'] + ' ' + mentors_df['skills_expertise'] + ' ' + mentors_df['languages']
    mentees_df['mentee_profile'] = mentees_df['skills_needed'] + ' ' + mentees_df['current_skill_level'] + ' ' + mentees_df['learning_style'] + ' ' + mentees_df['expectations'] + ' ' + mentees_df['languages']

    vectorizer = TfidfVectorizer()

    mentor_profiles = vectorizer.fit_transform(mentors_df['mentor_profile'])
    mentee_profiles = vectorizer.transform(mentees_df['mentee_profile'])

    cosine_similarities = cosine_similarity(mentee_profiles, mentor_profiles)

    mentee_index = mentees_df.index[mentees_df['email'] == mentee_email][0]
    top_mentor_indices = cosine_similarities[mentee_index].argsort()[::-1][:top_n]
    top_mentor_emails = mentors_df.loc[top_mentor_indices, 'email'].tolist()
    return top_mentor_emails

def get_reg(mentor_email):
    if not firebase_admin._apps:
        cred = credentials.Certificate("credentials.json") 
        firebase_admin.initialize_app(cred, {"databaseURL": "https://limble-30e8a-default-rtdb.asia-southeast1.firebasedatabase.app/"})
    ref = db.reference('/')
    user_ref = ref.child('mentor') #or mentee
    details=user_ref.get()
    flag=0
    for i in details:
        if mentor_email==details[i]["email"]:
            return details[i]