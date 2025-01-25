#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from PyPDF2 import PdfReader
import re
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = "AIzaSyA-9-lTQTWdNM43YdOXMQwGKDy0SrMwo6c"  # Replace with your actual key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class LegalDocProcessor:
    def __init__(self):
        self.key_sections = {
            'parties': ['parties', 'between'],
            'effective_date': ['effective date', 'commencement'],
            'termination': ['termination', 'expiry'],
            'confidentiality': ['confidentiality', 'nda'],
            'payment_terms': ['payment', 'consideration'],
            'governing_law': ['governing law', 'jurisdiction']
        }

    def extract_text(self, uploaded_file):
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            return '\n'.join([page.extract_text() for page in reader.pages])
        else:
            raise ValueError("Only PDF files are supported")

    def find_sections(self, text):
        results = {}
        for section, keywords in self.key_sections.items():
            pattern = r'(?i)({}).*?(?=\n\s*\n|$)'.format('|'.join(keywords))
            match = re.search(pattern, text, re.DOTALL)
            if match:
                results[section] = match.group(0).strip()
        return results

    def analyze_with_gemini(self, text, prompt):
        try:
            response = model.generate_content(prompt + text)
            return response.text
        except Exception as e:
            return f"API Error: {str(e)}"

class LegalAIAgent:
    def __init__(self):
        self.processor = LegalDocProcessor()
    
    def analyze_document(self, uploaded_file):
        text = self.processor.extract_text(uploaded_file)
        sections = self.processor.find_sections(text)
        
        analysis = {
            'metadata': self._get_metadata(text),
            'key_clauses': {},
            'risks': self._identify_risks(text)
        }
        
        for section, content in sections.items():
            analysis['key_clauses'][section] = {
                'summary': self._summarize_clause(content, section),
                'obligations': self._extract_obligations(content),
                'dates': self._extract_dates(content)
            }
        
        return analysis

    def _summarize_clause(self, text, section_name):
        prompt = f"Summarize this {section_name.replace('_', ' ')} clause in 3 bullet points:\n"
        return self.processor.analyze_with_gemini(text, prompt)

    def _extract_obligations(self, text):
        prompt = "List all party obligations from this legal clause:\n"
        return self.processor.analyze_with_gemini(text, prompt)

    def _extract_dates(self, text):
        prompt = "Extract all critical dates and deadlines in YYYY-MM-DD format:\n"
        return self.processor.analyze_with_gemini(text, prompt)

    def _get_metadata(self, text):
        prompt = """Extract metadata from this legal document:
        - Parties involved
        - Effective date
        - Document type
        - Key stakeholders
        Format as JSON:"""
        return self.processor.analyze_with_gemini(text, prompt)

    def _identify_risks(self, text):
        prompt = """Identify potential legal risks in this document:
        - Unbalanced obligations
        - Ambiguous terms
        - Compliance issues
        Format as bullet points:"""
        return self.processor.analyze_with_gemini(text, prompt)

# Streamlit UI
st.set_page_config(page_title="Legal Document AI Agent", layout="wide")
st.title("📄 PDF Legal Document Analyzer (Gemini)")
st.write("Upload your PDF legal document for analysis")

uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

if uploaded_file:
    agent = LegalAIAgent()
    
    with st.spinner('Analyzing document...'):
        try:
            analysis = agent.analyze_document(uploaded_file)
            
            st.success("Analysis complete!")
            st.divider()
            
            with st.expander("📋 Document Metadata", expanded=True):
                st.write(analysis['metadata'])
            
            with st.expander("📑 Key Clauses"):
                for section, content in analysis['key_clauses'].items():
                    st.subheader(f"{section.replace('_', ' ').title()}")
                    st.write("**Summary:**")
                    st.write(content['summary'])
                    st.write("**Obligations:**")
                    st.write(content['obligations'])
                    st.write("**Key Dates:**")
                    st.write(content['dates'])
                    st.divider()
            
            with st.expander("⚠️ Identified Risks"):
                st.write(analysis['risks'])
        
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")

