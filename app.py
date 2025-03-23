from flask import Flask, request, jsonify, render_template
import re
import random
import os
import traceback  # Added for better error tracking

app = Flask(__name__)

# Comprehensive knowledge base for all tomato diseases
tomato_diseases = {
    "bacterial_spot": {
        "symptoms": "Small, water-soaked spots on leaves, stems, and fruits that enlarge to dark brown spots with yellow halos. Severely infected leaves appear scorched and drop.",
        "treatment": "Remove infected plants, avoid overhead irrigation, apply copper-based bactericides, rotate crops, and use disease-free seeds."
    },
    "early_blight": {
        "symptoms": "Dark brown spots with concentric rings (target-like pattern) on lower leaves first. Infected leaves turn yellow and drop.",
        "treatment": "Remove infected leaves, improve air circulation, apply fungicides (chlorothalonil or copper-based), mulch around plants to prevent spore splash."
    },
    "late_blight": {
        "symptoms": "Irregular green-gray water-soaked spots on leaves, white fuzzy growth on leaf undersides, dark brown lesions on stems and fruits.",
        "treatment": "Remove infected plants immediately, apply fungicides preventatively (mancozeb, chlorothalonil), plant resistant varieties, avoid overhead watering."
    },
    "leaf_mold": {
        "symptoms": "Pale green to yellowish spots on upper leaf surfaces with olive-green to grayish-brown fuzzy mold on the undersides of leaves.",
        "treatment": "Improve greenhouse ventilation, reduce humidity below 85%, apply fungicides (chlorothalonil, mancozeb), remove and destroy infected plant debris."
    },
    "septoria_leaf_spot": {
        "symptoms": "Small, circular spots with dark margins and light gray centers. Tiny black dots (pycnidia) visible in the center of older spots.",
        "treatment": "Remove infected leaves, maintain good airflow, apply fungicides (chlorothalonil, copper-based), practice crop rotation, mulch soil surface."
    },
    "spider_mites": {
        "symptoms": "Fine yellow or white speckles on upper leaf surfaces, webbing on undersides of leaves, leaves become bronzed and dry, plants appear dusty.",
        "treatment": "Spray plants with water to dislodge mites, apply insecticidal soap or neem oil, introduce predatory mites, increase humidity around plants."
    },
    "target_spot": {
        "symptoms": "Brown circular spots with concentric rings on leaves, stems, and fruits. Similar to early blight but can affect all parts of the plant.",
        "treatment": "Prune lower leaves, improve air circulation, apply fungicides (mancozeb, chlorothalonil), avoid overhead irrigation, practice crop rotation."
    },
    "mosaic_virus": {
        "symptoms": "Mottled light and dark green patterns on leaves, leaf distortion, stunted growth, fruits show yellow rings or mottling.",
        "treatment": "No cure available. Remove and destroy infected plants, control aphids that spread the virus, wash hands after handling plants, use virus-resistant varieties."
    },
    "yellow_leaf_curl": {
        "symptoms": "Leaves curl upward and appear yellow at margins, plants are stunted, flowers drop, significantly reduced fruit production.",
        "treatment": "No cure for infected plants. Control whiteflies (the vector) with insecticides or yellow sticky traps, use resistant varieties, remove infected plants."
    }
}

# Define disease name variants for better matching
disease_name_variants = {
    "bacterial spot": ["bacterial spot", "bacterial", "bacteria"],
    "early blight": ["early blight", "early"],
    "late blight": ["late blight", "late"],
    "leaf mold": ["leaf mold", "mold"],
    "septoria leaf spot": ["septoria leaf spot", "septoria", "leaf spot"],
    "spider mites": ["spider mites", "spider", "mites"],
    "target spot": ["target spot", "target"],
    "mosaic virus": ["mosaic virus", "mosaic", "virus"],
    "yellow leaf curl": ["yellow leaf curl", "yellow", "leaf curl"]
}

# Convert to internal keys
disease_keys = {
    "bacterial spot": "bacterial_spot",
    "early blight": "early_blight",
    "late blight": "late_blight",
    "leaf mold": "leaf_mold",
    "septoria leaf spot": "septoria_leaf_spot",
    "spider mites": "spider_mites",
    "target spot": "target_spot",
    "mosaic virus": "mosaic_virus",
    "yellow leaf curl": "yellow_leaf_curl"
}

# Track conversation context
conversation_contexts = {}

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Print received data for debugging
        print("Received data:", request.data)
        
        data = request.get_json(force=True,silent=False)
        if not data:
            print("No JSON data received")
            return jsonify({"response": "No data received"}), 400
            
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        print(f"Processing message: '{user_message}' for session: {session_id}")
        
        if not user_message:
            print("No message in request")
            return jsonify({"response": "Please ask me something about tomato diseases."}), 400
        
        # Process the user message
        response = process_message(user_message.strip())
        
        print(f"Response: {response}")
        
        return jsonify({"response": response})
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in /chat route: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({"response": "I'm having trouble processing your request right now. Please try again."}), 500

def process_message(message):
    try:
        print(f"Processing message content: '{message}'")
        
        # Check for greetings
        if re.search(r'(?i)hello|hi|hey|greetings', message):
            return "Hello! How can I help with your tomato plants today?"
        
        # Check for thanks
        if re.search(r'(?i)thank you|thanks', message):
            return "You're welcome! Feel free to ask if you have more questions."

        # Special case for just "septoria" or similar short inputs
        if message.lower().strip() == "septoria":
            return f"Septoria Leaf Spot: {tomato_diseases['septoria_leaf_spot']['symptoms']} {tomato_diseases['septoria_leaf_spot']['treatment']}"
        
        # Check what diseases are mentioned - improved matching
        mentioned_disease = None
        
        # Debug what we're searching for
        print(f"Searching for disease in: '{message}'")
        
        # First, try to find disease mentions with improved pattern matching
        for disease_name, variants in disease_name_variants.items():
            for variant in variants:
                if variant.lower() in message.lower():
                    mentioned_disease = disease_name
                    print(f"Found disease: {disease_name} via variant: {variant}")
                    break
            if mentioned_disease:
                break
        
        if mentioned_disease:
            disease_key = disease_keys[mentioned_disease]
            print(f"Disease key: {disease_key}")
            
            # Determine what information is being requested
            if re.search(r'(?i)symptom', message):
                return f"Symptoms of {mentioned_disease}: {tomato_diseases[disease_key]['symptoms']}"
            elif re.search(r'(?i)treat|cure|fix|manage', message):
                return f"Treatment for {mentioned_disease}: {tomato_diseases[disease_key]['treatment']}"
            else:
                return f"{mentioned_disease.title()}: {tomato_diseases[disease_key]['symptoms']} {tomato_diseases[disease_key]['treatment']}"
        
        # Check for disease comparison
        comparison_match = re.search(r'(?i)difference between ([\w\s]+) and ([\w\s]+)', message)
        if comparison_match:
            disease1_mention = comparison_match.group(1).lower().strip()
            disease2_mention = comparison_match.group(2).lower().strip()
            
            disease1 = None
            disease2 = None
            
            # Find matching diseases
            for disease_name, variants in disease_name_variants.items():
                for variant in variants:
                    if variant in disease1_mention:
                        disease1 = disease_name
                    if variant in disease2_mention:
                        disease2 = disease_name
            
            if disease1 and disease2:
                disease1_key = disease_keys[disease1]
                disease2_key = disease_keys[disease2]
                
                return f"Differences between {disease1} and {disease2}:\n\n" \
                       f"{disease1.title()} symptoms: {tomato_diseases[disease1_key]['symptoms']}\n\n" \
                       f"{disease2.title()} symptoms: {tomato_diseases[disease2_key]['symptoms']}\n\n" \
                       f"{disease1.title()} treatment: {tomato_diseases[disease1_key]['treatment']}\n\n" \
                       f"{disease2.title()} treatment: {tomato_diseases[disease2_key]['treatment']}"
        
        # Check for diseases list request
        if re.search(r'(?i)what diseases|list diseases|diseases', message):
            return "I can provide information about: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Mosaic Virus, and Yellow Leaf Curl Virus."
        
        # Check for how to use
        if re.search(r'(?i)how (to|do I) use|instructions', message):
            return "You can ask me about specific tomato diseases like 'What are the symptoms of septoria leaf spot?' or 'How to treat early blight?' I can also compare diseases if you ask about the difference between them."
        
        # Default response
        return "I'm not sure I understand. You can ask me about specific tomato diseases like bacterial spot, early blight, septoria leaf spot, or ask for a list of diseases I know about."
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error processing message: {str(e)}")
        print(f"Traceback: {error_trace}")
        return "I'm having trouble understanding your question. Could you try phrasing it differently?"

if __name__ == '__main__':
    app.run(debug=True)