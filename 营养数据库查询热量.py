
NUTRITIONIX_APP_ID = "b18bc998"
NUTRITIONIX_APP_KEY = "5f319440ddb4bfc270fccf9c38a3ae7f"

# %%
import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import plotly.express as px

# File paths
PROFILE_FILE = "user_profiles.csv"
MEAL_LOG_FILE = "meal_logs.csv"
ACTIVITY_LOG_FILE = "activity_logs.csv"

# Nutritionix API credentials (replace with your actual keys)
APP_ID = "b18bc998"
APP_KEY = "5f319440ddb4bfc270fccf9c38a3ae7f"

# Helper Functions
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

def calculate_bmi(weight, height):
    bmi = weight / ((height / 100) ** 2)
    return bmi, get_bmi_category(bmi)

def calculate_daily_calorie_intake(weight, height, age, gender, activity_level):
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multiplier = {
        1: 1.2,    # Sedentary
        2: 1.375,  # Lightly Active
        3: 1.55,   # Moderately Active
        4: 1.725,  # Very Active
        5: 1.9     # Super Active
    }

    daily_calories_burned = bmr * activity_multiplier[activity_level]
    return bmr, daily_calories_burned

def calculate_recommended_calorie_intake(tdee, weight, target_weight, weeks):
    calorie_deficit_per_day = (weight - target_weight) * 7700 / (weeks * 7)
    recommended_calorie_intake = tdee - calorie_deficit_per_day
    return recommended_calorie_intake

def save_profile(username, profile_data):
    if not os.path.exists(PROFILE_FILE):
        profiles = pd.DataFrame(columns=["Username", "Age", "Gender", "Height", "Weight", "Target Weight", "Activity Level"])
    else:
        profiles = pd.read_csv(PROFILE_FILE)

    profiles = profiles[profiles["Username"] != username]  # Remove existing profile
    profiles = pd.concat([profiles, pd.DataFrame([profile_data])], ignore_index=True)
    profiles.to_csv(PROFILE_FILE, index=False)

def load_profile(username):
    if os.path.exists(PROFILE_FILE):
        profiles = pd.read_csv(PROFILE_FILE)
        user_profile = profiles[profiles["Username"] == username]
        if not user_profile.empty:
            return user_profile.iloc[0].to_dict()
    return None

def delete_profile(username):
    if os.path.exists(PROFILE_FILE):
        profiles = pd.read_csv(PROFILE_FILE)
        profiles = profiles[profiles["Username"] != username]
        profiles.to_csv(PROFILE_FILE, index=False)
        st.sidebar.info(f"Profile '{username}' deleted successfully!")

def log_meal(username, meal, calories):
    meal_logs = pd.read_csv(MEAL_LOG_FILE) if os.path.exists(MEAL_LOG_FILE) else pd.DataFrame(columns=["Username", "Meal", "Calories", "Timestamp"])
    new_log = {"Username": username, "Meal": meal, "Calories": calories, "Timestamp": pd.Timestamp.now()}
    meal_logs = pd.concat([meal_logs, pd.DataFrame([new_log])], ignore_index=True)
    meal_logs.to_csv(MEAL_LOG_FILE, index=False)

def log_activity(username, activity, calories):
    activity_logs = pd.read_csv(ACTIVITY_LOG_FILE) if os.path.exists(ACTIVITY_LOG_FILE) else pd.DataFrame(columns=["Username", "Activity", "Calories Burned", "Timestamp"])
    new_log = {"Username": username, "Activity": activity, "Calories Burned": calories, "Timestamp": pd.Timestamp.now()}
    activity_logs = pd.concat([activity_logs, pd.DataFrame([new_log])], ignore_index=True)
    activity_logs.to_csv(ACTIVITY_LOG_FILE, index=False)

def fetch_food_calories(description):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
        "Content-Type": "application/json"
    }
    data = {"query": description}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        calories = sum(item["nf_calories"] for item in result["foods"])
        return calories
    else:
        st.error("Failed to fetch calories. Please check your input or API credentials.")
        return None

def fetch_exercise_calories(exercise_description, weight):
    url = "https://trackapi.nutritionix.com/v2/natural/exercise"
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "query": exercise_description,
        "weight_kg": weight
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        calories_burned = sum(item["nf_calories"] for item in result["exercises"])
        return calories_burned
    else:
        st.error("Failed to fetch exercise calories. Please check your input or API credentials.")
        return None

# Streamlit App
st.title("Advanced Personal Nutrition and Fitness Tracker")

# User Authentication
st.sidebar.header("User Authentication")
username = st.sidebar.text_input("Enter Username")
profile_loaded = False

if username:
    profile = load_profile(username)
    if profile:
        st.sidebar.success(f"Welcome back, {username}!")
        profile_loaded = True
    else:
        st.sidebar.info(f"New user detected. Please set up your profile.")

# Profile Setup
st.header("Profile Setup" if not profile_loaded else "Update Profile")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age (years)", value=int(profile["Age"]) if profile_loaded else 25, min_value=1, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female"], index=0 if not profile_loaded else (0 if profile["Gender"] == "Male" else 1))
    height = st.number_input("Height (cm)", value=float(profile["Height"]) if profile_loaded else 170.0, min_value=50.0, max_value=250.0)
with col2:
    weight = st.number_input("Current Weight (kg)", value=float(profile["Weight"]) if profile_loaded else 70.0, min_value=20.0, max_value=200.0)
    target_weight = st.number_input("Target Weight (kg)", value=float(profile["Target Weight"]) if profile_loaded else 65.0, min_value=20.0, max_value=200.0)
    activity_level = st.selectbox("Exercise Habit Level", [1, 2, 3, 4, 5],
        format_func=lambda x: {
            1: "Sedentary",
            2: "Lightly Active",
            3: "Moderately Active",
            4: "Very Active",
            5: "Super Active",
        }[x],
        index=int(profile["Activity Level"]) - 1 if profile_loaded else 0
    )

if st.button("Save Profile"):
    save_profile(username, {"Username": username, "Age": age, "Gender": gender, "Height": height, "Weight": weight, "Target Weight": target_weight, "Activity Level": activity_level})
    st.success("Profile saved successfully!")

if st.sidebar.button("Delete Profile"):
    delete_profile(username)

# Calculate BMI and Recommended Calories
bmi, bmi_category = calculate_bmi(weight, height)
bmr, daily_calories_burned = calculate_daily_calorie_intake(weight, height, age, gender, activity_level)
weeks_to_target = 12  # Example: 12 weeks to reach target weight
recommended_calories = calculate_recommended_calorie_intake(daily_calories_burned, weight, target_weight, weeks_to_target)

st.sidebar.metric(label="BMI", value=f"{bmi:.1f}", delta=bmi_category)
st.sidebar.metric(label="BMR", value=f"{bmr:.0f} kcal/day")
st.sidebar.metric(label="Recommended Daily Calories Burned", value=f"{daily_calories_burned:.0f} kcal/day")
st.sidebar.metric(label="Recommended Daily Calorie Intake", value=f"{recommended_calories:.0f} kcal/day")

# Meal Logging
st.header("Log Meals")
meal_logging_method = st.selectbox("Select Meal Logging Method", ["Manual Entry", "Image Recognition", "Direct Calorie Input"])

if meal_logging_method == "Manual Entry":
    meal_description = st.text_input("Describe your meal (e.g., '1 apple and 2 slices of bread')")
    if st.button("Fetch and Log Meal Calories"):
        if meal_description:
            calories = fetch_food_calories(meal_description)
            if calories:
                st.write(f"Estimated Calories: {calories} kcal")
                log_meal(username, meal_description, calories)

elif meal_logging_method == "Image Recognition":
    st.write("Image recognition feature is not implemented yet. Please use another method.")

elif meal_logging_method == "Direct Calorie Input":
    meal_description = st.text_input("Describe your meal (e.g., 'Packaged snack')")
    calories = st.number_input("Enter Calories (kcal)", min_value=0)
    if st.button("Log Meal Calories"):
        if meal_description and calories > 0:
            st.write(f"Logged Calories: {calories} kcal")
            log_meal(username, meal_description, calories)

# Exercise Logging
st.header("Log Activities")
exercise_description = st.text_input("Describe your activity (e.g., 'Running for 30 minutes')")
if st.button("Fetch and Log Exercise Calories"):
    if exercise_description:
        burned_calories = fetch_exercise_calories(exercise_description, weight)
        if burned_calories:
            st.write(f"Estimated Calories Burned: {burned_calories} kcal")
            log_activity(username, exercise_description, burned_calories)

# Feedback Section
st.header("Feedback")
if os.path.exists(MEAL_LOG_FILE) and os.path.exists(ACTIVITY_LOG_FILE):
    meal_logs = pd.read_csv(MEAL_LOG_FILE)
    activity_logs = pd.read_csv(ACTIVITY_LOG_FILE)
    if not meal_logs.empty and not activity_logs.empty:
        total_calories_consumed = meal_logs["Calories"].sum()
        total_calories_burned = activity_logs["Calories Burned"].sum()

        calorie_balance = total_calories_burned - total_calories_consumed

        if calorie_balance > 0:
            st.success(f"Great job, {username}! You've burned {calorie_balance:.0f} more calories than you've consumed. Keep it up!")
        elif calorie_balance < 0:
            st.warning(f"Oops, {username}! You've consumed {abs(calorie_balance):.0f} more calories than you've burned. Time to hit the gym or watch your diet!")
        else:
            st.info(f"Well done, {username}! You've balanced your calorie intake and expenditure perfectly.")

        # Provide feedback on recommended calorie intake
        if total_calories_consumed > recommended_calories:
            st.warning(f"You're consuming more calories ({total_calories_consumed:.0f} kcal) than recommended ({recommended_calories:.0f} kcal). Consider adjusting your diet.")
        else:
            st.success(f"Your calorie intake ({total_calories_consumed:.0f} kcal) is within the recommended range ({recommended_calories:.0f} kcal). Keep it up!")

# Visual Graphs for Weight Change, Calorie Trends, and Streaks
st.header("Visual Graphs")

# Weight Change Graph
if os.path.exists(PROFILE_FILE):
    profiles = pd.read_csv(PROFILE_FILE)
    if not profiles.empty:
        weight_change_fig = px.line(profiles, x="Username", y="Weight", title="Weight Change Over Time")
        st.plotly_chart(weight_change_fig)

# Calorie Trends Graph
if os.path.exists(MEAL_LOG_FILE):
    meal_logs = pd.read_csv(MEAL_LOG_FILE)
    if not meal_logs.empty:
        calorie_trends_fig = px.line(meal_logs, x="Timestamp", y="Calories", title="Calorie Intake Trends Over Time")
        st.plotly_chart(calorie_trends_fig)

# Streaks, Badges, and Rewards
st.header("Streaks, Badges, and Rewards")

if os.path.exists(MEAL_LOG_FILE) and os.path.exists(ACTIVITY_LOG_FILE):
    meal_logs = pd.read_csv(MEAL_LOG_FILE)
    activity_logs = pd.read_csv(ACTIVITY_LOG_FILE)
    if not meal_logs.empty and not activity_logs.empty:
        meal_logs["Timestamp"] = pd.to_datetime(meal_logs["Timestamp"])
        activity_logs["Timestamp"] = pd.to_datetime(activity_logs["Timestamp"])

        meal_streak = meal_logs["Timestamp"].diff().dt.days.le(1).sum()
        activity_streak = activity_logs["Timestamp"].diff().dt.days.le(1).sum()

        st.write(f"Meal Logging Streak: {meal_streak} days")
        st.write(f"Activity Logging Streak: {activity_streak} days")

        if meal_streak >= 7:
            st.success("🏅 1 Week Meal Logging Streak!")
        if activity_streak >= 7:
            st.success("🏅 1 Week Activity Logging Streak!")
        if meal_streak >= 30:
            st.success("🏆 1 Month Meal Logging Streak!")
        if activity_streak >= 30:
            st.success("🏆 1 Month Activity Logging Streak!")


