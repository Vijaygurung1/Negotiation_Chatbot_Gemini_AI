import streamlit as st
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download necessary NLTK resources
nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Price range
high_price = 100000  # Max price
min_price = 60000  # Min price


# Function to perform sentiment analysis
def get_sentiment(user_input):
    sentiment_scores = sia.polarity_scores(user_input)
    compound_score = sentiment_scores['compound']

    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'


# Function to interact with Gemini API
def interact_with_gemini_api(prompt):
    api_url = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5-bison:generateText"

    # Define the payload for the POST request
    data = {
        "prompt": {
            "text": prompt
        },
        "temperature": 0.7  # Optional: Adjusts the creativity/randomness of the responses
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer AIzaSyB5MCzipnJzWC_gB3qbDnzEoDWpYc-lnNw"  # Replace with your actual API key
    }

    # Send the POST request to the Gemini API
    response = requests.post(api_url, headers=headers, json=data)

    # Handle the API response
    if response.status_code == 200:
        api_response = response.json()
        # Extract the content from the API response
        return api_response.get("candidates", [{}])[0].get("output", "Chatbot: Sorry, I couldn't understand that.")
    else:
        # Return the error if the API request fails
        return f"Chatbot: Error {response.status_code}. {response.text}"


# Function to extract price from user input
def extract_price(user_input):
    words = user_input.split()
    for word in words:
        if word.startswith('₹') and word[1:].isdigit():
            return int(word[1:])
        elif word.isdigit():
            return int(word)
    return None


# Function to simulate negotiation
def negotiate(user_input):
    sentiment = get_sentiment(user_input)

    if "starting price" in user_input.lower():
        return "Chatbot: The starting price for this product is ₹75,000. What would you like to offer or discuss?"

    if "discount" in user_input.lower():
        return "Chatbot: I’m glad you’re interested! We’re currently discussing a product with a price range between ₹60,000 and ₹1,00,000. What’s your target price?"

    if "best price" in user_input.lower():
        if sentiment == 'positive':
            return "Chatbot: Since you're interested, I can offer you a discount. How about ₹70,000?"
        else:
            return "Chatbot: I understand you're asking for a discount. I can offer ₹75,000."

    if "feel" in user_input.lower() and "too high" in user_input.lower():
        return "Chatbot: I understand ₹70,000 might seem high. How about we settle at ₹65,000?"

    if "negotiate" in user_input.lower() or "meet halfway" in user_input.lower():
        offer_price = extract_price(user_input)
        if offer_price:
            if offer_price >= high_price:
                return "Chatbot: I appreciate your offer, but ₹75,000 is the best I can do."
            elif offer_price >= min_price:
                return f"Chatbot: We could meet at ₹{offer_price + 5000}. What do you think?"
            else:
                return f"Chatbot: ₹{offer_price} is too low. The minimum price I can offer is ₹{min_price}."
        else:
            return "Chatbot: Could you please specify your offer?"

    if "settle" in user_input.lower() or "negotiation" in user_input.lower():
        return interact_with_gemini_api(user_input)

    if "interested" in user_input.lower() and sentiment == 'positive':
        return "Chatbot: I’m glad to hear you're interested! Since you're being positive, I can offer you a special discount. How does ₹65,000 sound?"

    if "concern" in user_input.lower() and sentiment == 'negative':
        return "Chatbot: I understand your concern. I can offer a price of ₹70,000, which is the best I can do."

    return "Chatbot: How can I assist you further with the pricing?"


# Streamlit App
st.title("Negotiation Chatbot with Gemini API")

# Get user input
user_input = st.text_input("You:", "What would you like to negotiate about?")

# Define chatbot response
if user_input:
    response = negotiate(user_input)
    st.text_area("Chatbot:", value=response, height=200)
