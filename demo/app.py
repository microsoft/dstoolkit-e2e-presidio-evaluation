import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import OperatorConfig

def generate_sample_data():
    """Generate sample data with various PII elements"""
    data = []
    
    # Sample data templates
    names = ["John Smith", "Sarah Johnson", "Michael Brown", "Emma Davis", 
            "Robert Wilson", "Maria Garcia", "David Lee", "Jennifer Taylor"]
    titles = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
    locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX"]
    emails = [f"{name.lower().replace(' ', '.')}@email.com" for name in names]
    phones = [f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}" 
             for _ in range(8)]
    
    # Generate records
    for _ in range(10):
        name = random.choice(names)
        record = {
            'Title': random.choice(titles),
            'Full Name': name,
            'Email': random.choice(emails),
            'Phone': random.choice(phones),
            'Address': random.choice(locations),
            'Date': (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            'Transaction Amount': round(random.uniform(100, 10000), 2)
        }
        data.append(record)
    
    return pd.DataFrame(data)

class PresidioDemo:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.deanonymizer = DeanonymizeEngine()
    
    def add_custom_recognizer(self):
        """Add custom recognizer for titles"""
        titles_list = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
        titles_recognizer = PatternRecognizer(
            supported_entity="TITLE",
            deny_list=titles_list
        )
        self.analyzer.registry.add_recognizer(titles_recognizer)
        return titles_recognizer
    
    def analyze_text(self, text, entities=None):
        """Analyze text for PII"""
        if entities is None:
            entities = ["PERSON", "LOCATION", "EMAIL_ADDRESS", "PHONE_NUMBER", 
                       "DATE_TIME", "TITLE"]
        return self.analyzer.analyze(text=text, language='en', entities=entities)
    
    def display_pii_results(self, text, results):
        """Display PII detection results in columns"""
        # Group results by entity type
        grouped_results = {}
        for result in results:
            entity_type = result.entity_type
            if entity_type not in grouped_results:
                grouped_results[entity_type] = []
            grouped_results[entity_type].append({
                'text': text[result.start:result.end],
                'score': result.score
            })
        
        # Display results in columns
        cols = st.columns(3)
        for idx, (entity_type, items) in enumerate(grouped_results.items()):
            with cols[idx % 3]:
                st.subheader(f"📌 {entity_type}")
                for item in items:
                    st.write(f"• '{item['text']}' (confidence: {item['score']:.2f})")
        
        return grouped_results
    
    def anonymize_text(self, text, results, method="replace"):
        """Anonymize detected PII in text"""
        operators = {}
        
        if method == "replace":
            operator_mapping = {
                "PERSON": "<PERSON>",
                "LOCATION": "<LOCATION>",
                "EMAIL_ADDRESS": "<EMAIL>",
                "PHONE_NUMBER": "<PHONE>",
                "DATE_TIME": "<DATE>",
                "TITLE": "<TITLE>"
            }
            
            for result in results:
                operators[result.entity_type] = OperatorConfig(
                    "replace", 
                    {"new_value": operator_mapping.get(result.entity_type, "<ANONYMIZED>")}
                )
        else:  # encrypt
            encryption_key = "WmZq4t7w!z%C&F)J"
            for result in results:
                operators[result.entity_type] = OperatorConfig(
                    "encrypt", 
                    {"key": encryption_key}
                )
        
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        
        return anonymized.text

def main():
    st.set_page_config(page_title="Presidio PII Demo", layout="wide")
    st.title("PII Detection and Anonymization with Presidio")
    
    # Initialize Presidio Demo
    demo = PresidioDemo()
    demo.add_custom_recognizer()
    
    # Initialize session state variables if they don't exist
    if 'detection_performed' not in st.session_state:
        st.session_state.detection_performed = False
    if 'grouped_results' not in st.session_state:
        st.session_state.grouped_results = None
    
    # Sidebar for data input options
    st.sidebar.header("Data Input Options")
    input_option = st.sidebar.radio(
        "Choose input method:",
        ["Generate Sample Data", "Upload File"]
    )
    
    # Data input section
    st.header("1. Data Input")
    if input_option == "Generate Sample Data":
        if st.button("Generate New Sample Data"):
            st.session_state.df = generate_sample_data()
            st.session_state.text = st.session_state.df.to_string()
            # Reset detection state when new data is generated
            st.session_state.detection_performed = False
            st.session_state.grouped_results = None
    else:
        uploaded_file = st.file_uploader("Upload a text file", type=['txt', 'csv'])
        if uploaded_file:
            if uploaded_file.type == "text/csv":
                st.session_state.df = pd.read_csv(uploaded_file)
                st.session_state.text = st.session_state.df.to_string()
                # Reset detection state when new file is uploaded
                st.session_state.detection_performed = False
                st.session_state.grouped_results = None
            else:
                st.session_state.text = uploaded_file.getvalue().decode()
    
    # Display input data
    if 'text' in st.session_state:
        st.subheader("Input Data:")
        st.text_area("Original Text", st.session_state.text, height=200)
        
        # PII Detection
        st.header("2. PII Detection")
        if st.button("Detect PII"):
            results = demo.analyze_text(st.session_state.text)
            st.session_state.results = results
            
            # Group results by entity type
            grouped_results = {}
            for result in results:
                entity_type = result.entity_type
                if entity_type not in grouped_results:
                    grouped_results[entity_type] = []
                grouped_results[entity_type].append({
                    'text': st.session_state.text[result.start:result.end],
                    'score': result.score
                })
            
            # Display results in columns
            cols = st.columns(3)
            for idx, (entity_type, items) in enumerate(grouped_results.items()):
                with cols[idx % 3]:
                    st.subheader(f"📌 {entity_type}")
                    for item in items:
                        st.write(f"• '{item['text']}' (confidence: {item['score']:.2f})")
        
        # PII Anonymization
        st.header("3. PII Anonymization")
        if 'results' in st.session_state:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Anonymize (Replace)"):
                    anonymized = demo.anonymize_text(
                        st.session_state.text, 
                        st.session_state.results,
                        "replace"
                    )
                    st.text_area("Anonymized Text (Replaced)", anonymized, height=200)
            
            with col2:
                if st.button("Anonymize (Encrypt)"):
                    anonymized = demo.anonymize_text(
                        st.session_state.text, 
                        st.session_state.results,
                        "encrypt"
                    )
                    st.text_area("Anonymized Text (Encrypted)", anonymized, height=200)

if __name__ == "__main__":
    main() 