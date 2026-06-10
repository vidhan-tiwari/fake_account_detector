import streamlit as st
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import instaloader
import re

# loading model and  scaler 

@st.cache_resource
def load_assets():
    try:
        model = load_model('instagram_fake_detector_ANN.h5')
        scaler = joblib.load('scaler_ANN.pkl') 
        return model, scaler
    except Exception as e:
        st.error(f"Error loading model or scaler: {e}")
        return None, None

model, scaler = load_assets()

# Feature engineering helper function

def extract_features(username, fullname, desc_len, has_url, is_private, has_pic, posts, followers, follows):
    """
    converts user inputs into 11 features accepted in ANN model.
    correct order of input features:
    ['profile pic', 'nums/length username', 'fullname words', 'nums/length fullname', 
     'name==username', 'description length', 'external URL', 'private', '#posts', 
     '#followers', '#follows']
    """
    
    # 1. profile_picture presence
    input_has_pic = 1 if has_pic else 0
    
    # 2. nums/length_username ratio
    user_len = len(username)
    user_nums = sum(c.isdigit() for c in username)
    input_username_ratio = user_nums / user_len if user_len > 0 else 0
    
    # 3. fullname words
    # Remove extra spaces and count words
    input_fullname_words = len(fullname.strip().split()) if fullname else 0
    
    # 4. nums/length_fullname ratio
    full_len = len(fullname)
    full_nums = sum(c.isdigit() for c in fullname)
    input_fullname_ratio = full_nums / full_len if full_len > 0 else 0
    
    # 5. name==username (0 or 1) binary class
    input_name_equals_user = 1 if username.lower() == fullname.lower() else 0
    
    # 6. description length or bio length
    input_desc_len = int(desc_len)
    
    # 7. external URL (0 or 1) binary class
    input_has_url = 1 if has_url else 0
    
    # 8. private (0 or 1) binary class
    input_is_private = 1 if is_private else 0
    
    # 9, 10, 11.
    input_num_posts = int(posts)
    input_num_followers = int(followers)
    input_num_follows = int(follows)
    
    # Create the array in the exact order
    features = np.array([
        input_has_pic, 
        input_username_ratio, 
        input_fullname_words, 
        input_fullname_ratio,
        input_name_equals_user, 
        input_desc_len, 
        input_has_url, 
        input_is_private, 
        input_num_posts, 
        input_num_followers, 
        input_num_follows
    ])
    
    # Reshaping into 2D matrix 
    return features.reshape(1, -1)

# model predition function
def make_prediction(features_mat):
    if model is None or scaler is None:
        st.error("Model/Scaler not loaded.")
        return

    # scaling the features
    scaled_features = scaler.transform(features_mat)
    
    # model prediction
    prediction_prob = model.predict(scaled_features)
    
    #  sigmoid output: < 0.5 is Real (0), > 0.5 is Fake (1)
    is_fake = prediction_prob[0][0] > 0.5 
    
    return is_fake, prediction_prob[0][0]

# streamlit UI function
st.title("🕵️ Instagram Fake Account Detector")
st.markdown("Use this tool to analyze Instagram accounts using Deep Learning.")

# Tabs for selection
tab1, tab2 = st.tabs(["AUTOMATIC PATHWAY ","MANUAL-DATA-ENTRY-PATHWAY"])


with tab2:
    st.header("Manual Data Entry.")
    st.write("Enter the profile details manually:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        m_username = st.text_input("Username", placeholder="e.g. vidh.an__01")
        m_fullname = st.text_input("Full Name", placeholder="e.g. Vidhan Tiwari")
        
        bio_input = st.text_input("Bio (Paste text OR enter length)", placeholder="e.g. 'I love travel' OR '150'")
        if bio_input.strip().isdigit():
            m_desc_len = int(bio_input.strip())
        else:
            m_desc_len = len(bio_input)
            
        m_posts = st.number_input("Number of Posts", min_value=0, value=0)
        
    with col2:
        m_followers = st.number_input("Number of Followers", min_value=0, value=0)
        m_follows = st.number_input("Number Following", min_value=0, value=0)
        
        st.write("---")
        m_has_pic = st.checkbox("Has Profile Picture?", value=True)
        m_is_private = st.checkbox("Is Private Account?", value=False)
        m_has_url = st.checkbox("Has External URL in Bio?", value=False)
        m_is_verified = st.checkbox("Has Blue Tick (Verified)?", value=False)
        st.caption("ℹ️ **Note:** Selecting this bypasses the AI model. Leave unchecked if you want to see the model's output.")

    if st.button("Predict (Manual)"):
         
        if m_is_verified:
            # blue tick model by pass
            st.divider()
            st.info("ℹ️ Blue Tick detected.")
            st.success(f"✅ The account **@{m_username}** is Verified. It is definitely **REAL**.")
        
        else:
            # missing field validation check
            missing_fields = []
            
            # Check strings specifically because they cannot be empty for feature calculations
            if not m_username.strip():
                missing_fields.append("Username")
            if not m_fullname.strip():
                missing_fields.append("Full Name")
    
            if missing_fields:
                st.error(f"⚠️ Missing required fields: {', '.join(missing_fields)}")
                st.info("The model requires these fields to calculate text ratios (e.g., nums/length).")
            else:
                try:
                    input_features = extract_features(
                        m_username, m_fullname, m_desc_len, m_has_url, 
                        m_is_private, m_has_pic, m_posts, m_followers, m_follows
                    )
                    
                    is_fake, prob = make_prediction(input_features)
                    
                    st.divider()
                    if is_fake:
                        st.error(f"🚨 This account is likely **FAKE** ({prob:.2%} probability)")
                    else:
                        st.success(f"✅ This account is likely **REAL** ({(1-prob):.2%} confidence)")
                except Exception as e:
                    st.error(f"An error occurred during prediction: {e}")


# automated instaloader path
with tab1:
    st.header("Automatic Fetching")
    st.info("Note: Instagram blocks frequent anonymous requests. If this fails, use Manual Entry.")
    
    target_username = st.text_input("Enter Target Username for Auto-Scan")
    
    if st.button("Fetch & Predict"):
        if not target_username:
            st.warning("Please enter a username.")
        else:
            status_placeholder = st.empty()
            status_placeholder.text("Connecting to Instagram...")
            
            try:
                L = instaloader.Instaloader()
                
                profile = instaloader.Profile.from_username(L.context, target_username)
                
                status_placeholder.text("Data fetched! Processing...")
                
                i_username = profile.username
                i_fullname = profile.full_name if profile.full_name else ""
                i_desc_len = len(profile.biography) if profile.biography else 0
                i_has_url = True if profile.external_url else False
                i_is_private = profile.is_private
                i_has_pic = True if profile.profile_pic_url else False
                i_is_verified = profile.is_verified
                i_posts = profile.mediacount
                i_followers = profile.followers
                i_follows = profile.followees
                
                with st.expander("View Fetched Data"):
                    st.json({
                        "Username": i_username,
                        "Full Name": i_fullname,
                        "Bio Length": i_desc_len,
                        "External URL": i_has_url,
                        "Private": i_is_private,
                        "Profile Pic": i_has_pic,
                        "Posts": i_posts,
                        "Followers": i_followers,
                        "Following": i_follows
                    })

                status_placeholder.empty() # Clear status

                st.divider()
                
                 # LOGIC CHECK FOR BLUE TICK
                if i_is_verified:
                    st.info("ℹ️ Instagram API confirms this account has a Blue Tick.")
                    st.success(f"✅ The account **@{i_username}** is Verified. It is definitely **REAL**.")
                else:
                    input_features = extract_features(
                    i_username, i_fullname, i_desc_len, i_has_url, 
                    i_is_private, i_has_pic, i_posts, i_followers, i_follows
                    )
                
                    # Predict
                    is_fake, prob = make_prediction(input_features)
                    if is_fake:
                        st.error(f"🚨 This account is likely **FAKE** ({prob:.2%} probability)")
                    else:
                        st.success(f"✅ This account is likely **REAL** ({(1-prob):.2%} confidence)")
                    
            except instaloader.ConnectionException:
                status_placeholder.empty()
                st.error("Connection Error: Instagram refused the connection. Try again later or use Manual Entry.")
            except instaloader.LoginRequiredException:
                status_placeholder.empty()
                st.error("Login Error: Instagram requires login to view this profile. Please use Manual Entry.")
            except Exception as e:
                status_placeholder.empty()
                st.error(f"An unexpected error occurred: {e}")
        









