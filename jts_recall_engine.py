#!/usr/bin/env python3
"""
JTS Recall Engine for Pi2
Lightweight, fast recall engine that listens to medics' voice input and returns clinical advice
using preloaded JTS PDFs — completely offline on a Raspberry Pi 2.

Components:
1. JTS PDF Parsing + Corpus Preprocessing
2. BM25 Indexing (Build-Time)
3. STT Input (Runtime)
4. Query Matching + Response
5. TTS Output (Festival with MBROLA voices)
"""

import json
import os
import logging
import time
from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi
from vosk import Model, KaldiRecognizer
import pyaudio
import subprocess
import platform
from tts_utils import speak
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VitalSignsAnalyzer:
    """Analyze vital signs and provide treatment recommendations"""
    
    def __init__(self):
        # Normal vital ranges
        self.normal_ranges = {
            'hr': {'min': 60, 'max': 100, 'critical_low': 50, 'critical_high': 120},
            'bp_systolic': {'min': 90, 'max': 140, 'critical_low': 80, 'critical_high': 180},
            'bp_diastolic': {'min': 60, 'max': 90, 'critical_low': 50, 'critical_high': 110},
            'rr': {'min': 12, 'max': 20, 'critical_low': 8, 'critical_high': 30},
            'spo2': {'min': 95, 'max': 100, 'critical_low': 90, 'critical_high': 100},
            'temp': {'min': 36.5, 'max': 37.5, 'critical_low': 35, 'critical_high': 39}
        }
    
    def analyze_vitals(self, vitals: Dict) -> Dict:
        """Analyze current vitals and return assessment"""
        assessment = {
            'status': 'normal',
            'concerns': [],
            'recommendations': [],
            'critical': False
        }
        
        # Check each vital
        for vital, value in vitals.items():
            if vital in self.normal_ranges:
                ranges = self.normal_ranges[vital]
                
                if value < ranges['critical_low'] or value > ranges['critical_high']:
                    assessment['critical'] = True
                    assessment['status'] = 'critical'
                    assessment['concerns'].append(f"{vital.upper()}: {value} (CRITICAL)")
                    
                    # Add specific recommendations
                    if vital == 'hr' and value < ranges['critical_low']:
                        assessment['recommendations'].append("Consider atropine 1mg IV for bradycardia")
                    elif vital == 'hr' and value > ranges['critical_high']:
                        assessment['recommendations'].append("Monitor for shock, consider fluid resuscitation")
                    elif vital == 'bp_systolic' and value < ranges['critical_low']:
                        assessment['recommendations'].append("Consider fluid resuscitation, monitor for shock")
                    elif vital == 'spo2' and value < ranges['critical_low']:
                        assessment['recommendations'].append("Administer oxygen, consider airway intervention")
                        
                elif value < ranges['min'] or value > ranges['max']:
                    assessment['concerns'].append(f"{vital.upper()}: {value} (abnormal)")
        
        return assessment
    
    def get_treatment_recommendation(self, vitals: Dict, query: str) -> str:
        """Get treatment recommendation based on vitals and query"""
        assessment = self.analyze_vitals(vitals)
        
        # If critical vitals, prioritize stabilization
        if assessment['critical']:
            if assessment['recommendations']:
                return f"CRITICAL: {assessment['concerns'][0]}. {assessment['recommendations'][0]}"
            else:
                return f"CRITICAL: {assessment['concerns'][0]}. Stabilize patient first."
        
        # Check for specific vital-based contraindications
        if 'hr' in vitals and vitals['hr'] > 120:
            if 'epinephrine' in query.lower():
                return "Tachycardia present. Consider alternative to epinephrine."
        
        if 'bp_systolic' in vitals and vitals['bp_systolic'] > 180:
            if 'epinephrine' in query.lower():
                return "Severe hypertension. Consider alternative to epinephrine."
        
        if 'spo2' in vitals and vitals['spo2'] < 95:
            if any(drug in query.lower() for drug in ['morphine', 'fentanyl']):
                return "Low oxygen saturation. Monitor respiratory depression closely."
        
        # If vitals are normal, proceed with normal treatment
        return "Vitals acceptable. Proceed with treatment."

class JTSCorpusProcessor:
    """Process JTS PDFs into structured corpus for BM25 indexing"""
    
    def __init__(self, jts_data_dir: str = "jts_data"):
        self.jts_data_dir = jts_data_dir
        self.corpus_file = "jts_corpus.json"
        
    def load_existing_corpus(self) -> List[Dict]:
        """Load existing processed JTS data and convert to corpus format"""
        corpus = []
        
        # Load all JSON files from jts_data directory
        for filename in os.listdir(self.jts_data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.jts_data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Convert to corpus format
                    for doc_id, doc_data in data.items():
                        if isinstance(doc_data, dict) and 'sections' in doc_data:
                            # Process sections - include all sections, not just overview
                            for section_name, section_text in doc_data['sections'].items():
                                if section_text and len(section_text.strip()) > 30:  # Lower minimum length
                                    corpus.append({
                                        "section": section_name,
                                        "source": doc_data.get('filename', doc_id),
                                        "text": section_text.strip(),
                                        "page": 0,
                                        "category": doc_data.get('category', 'general')
                                    })
                        elif isinstance(doc_data, dict) and 'full_text' in doc_data:
                            # Process full text - split into smaller chunks for better search
                            full_text = doc_data['full_text']
                            if full_text and len(full_text.strip()) > 50:
                                # Split into smaller paragraphs for better search
                                paragraphs = [p.strip() for p in full_text.split('\n\n') if len(p.strip()) > 30]
                                for i, para in enumerate(paragraphs[:50]):  # Increase limit to 50 paragraphs
                                    corpus.append({
                                        "section": f"paragraph_{i+1}",
                                        "source": doc_data.get('filename', doc_id),
                                        "text": para,
                                        "page": 0,
                                        "category": "general"
                                    })
                                    
                except Exception as e:
                    logger.warning(f"Error processing {filename}: {e}")
                    continue
                    
        logger.info(f"Loaded {len(corpus)} corpus entries")
        return corpus
    
    def save_corpus(self, corpus: List[Dict]) -> None:
        """Save corpus to JSON file"""
        with open(self.corpus_file, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved corpus to {self.corpus_file}")

class JTSRecallEngine:
    """Main JTS Recall Engine with BM25 indexing and voice interface"""
    
    def __init__(self):
        self.corpus = []
        self.bm25 = None
        self.stt_model = None
        self.vital_analyzer = VitalSignsAnalyzer()
        self.patient_context = {
            'weight': None,
            'allergies': [],
            'medications': [],
            'conditions': [],
            'vitals': {},
            'vital_history': [],  # Track vitals over time
            'contraindications': [],
            'last_vital_check': None,
            'critical_patient': False
        }
        self.conversation_history = []
        self.corpus_processor = JTSCorpusProcessor()
        
    def initialize(self) -> None:
        """Initialize the recall engine"""
        logger.info("Initializing JTS Recall Engine...")
        
        # Load comprehensive corpus (prioritized over all others)
        if os.path.exists("jts_comprehensive_corpus.json"):
            logger.info("Loading comprehensive JTS corpus...")
            with open("jts_comprehensive_corpus.json", 'r', encoding='utf-8') as f:
                self.corpus = json.load(f)
        elif os.path.exists("jts_focused_corpus.json"):
            logger.info("Loading focused clinical corpus...")
            with open("jts_focused_corpus.json", 'r', encoding='utf-8') as f:
                self.corpus = json.load(f)
        elif os.path.exists("jts_rescue_medicine_cleaned.json"):
            logger.info("Loading existing corpus...")
            with open("jts_rescue_medicine_cleaned.json", 'r', encoding='utf-8') as f:
                self.corpus = json.load(f)
        else:
            logger.error("No corpus files found! Please run comprehensive_jts_processor.py first to create comprehensive corpus.")
            raise FileNotFoundError("No corpus files found")
        
        # Build BM25 index
        logger.info("Building BM25 index...")
        self._build_bm25_index()
        
        # Load STT model
        logger.info("Loading Vosk STT model...")
        self._load_stt_model()
        
        logger.info("JTS Recall Engine initialized successfully!")
        
    def _build_bm25_index(self) -> None:
        """Build BM25 index from corpus using rank_bm25"""
        if not self.corpus:
            raise ValueError("No corpus available for indexing")
            
        logger.info("Building BM25 index...")
        
        # Tokenize paragraphs for BM25
        tokenized = []
        for p in self.corpus:
            # Clean and tokenize text
            text = p["text"].lower()
            # Remove extra whitespace and split
            tokens = re.sub(r'\s+', ' ', text).strip().split()
            tokenized.append(tokens)
        
        # Build BM25 index using rank_bm25
        self.bm25 = BM25Okapi(tokenized)
        logger.info(f"BM25 index built with {len(self.corpus)} documents")
        
    def _load_stt_model(self) -> None:
        """Load Vosk STT model"""
        model_path = "models/vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
        
        self.stt_model = Model(model_path)
        logger.info("Vosk STT model loaded successfully")
        
    def get_best_microphone(self) -> Optional[int]:
        """Get the best available microphone"""
        p = pyaudio.PyAudio()
        best_device = None
        
        # Look for built-in microphone first (usually more reliable)
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Has input capability
                name = info['name'].lower()
                # Prefer built-in microphone
                if 'imac' in name or 'built-in' in name or 'internal' in name:
                    best_device = i
                    break
                # Fallback to any input device
                elif best_device is None:
                    best_device = i
        
        p.terminate()
        return best_device
        
    def listen_for_query(self) -> str:
        """Listen for voice query using Vosk STT with improved audio processing"""
        if not self.stt_model:
            raise RuntimeError("STT model not loaded")
            
        rec = KaldiRecognizer(self.stt_model, 16000)
        rec.SetWords(True)  # Enable word timing for better accuracy
        
        # Get best microphone
        mic_device = self.get_best_microphone()
        if mic_device is None:
            logger.error("No microphone found!")
            return ""
        
        logger.info(f"Using microphone device: {mic_device}")
        
        p = pyaudio.PyAudio()
        mic = p.open(
            format=pyaudio.paInt16, 
            channels=1,
            rate=16000, 
            input=True, 
            input_device_index=mic_device,
            frames_per_buffer=4096  # Smaller buffer for more responsive recognition
        )
        
        logger.info("🎤 Listening... (speak clearly)")
        
        try:
            silence_frames = 0
            max_silence_frames = 30  # About 2 seconds of silence
            audio_buffer = []
            
            while True:
                data = mic.read(2048, exception_on_overflow=False)
                audio_buffer.append(data)
                
                # Process audio in larger chunks for better recognition
                if len(audio_buffer) >= 3:  # Process every 3 chunks
                    combined_data = b''.join(audio_buffer)
                    audio_buffer = []
                    
                    if rec.AcceptWaveform(combined_data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip()
                        if text:  # Only return if we got actual text
                            return text
                    else:
                        # Check for partial results to detect speech
                        partial = json.loads(rec.PartialResult())
                        partial_text = partial.get('partial', '').strip()
                        if partial_text:
                            silence_frames = 0
                        else:
                            silence_frames += 1
                    
                    # Stop if too much silence
                    if silence_frames > max_silence_frames:
                        break
                        
        except KeyboardInterrupt:
            logger.info("\n🛑 Listening stopped")
            return ""
        finally:
            mic.stop_stream()
            mic.close()
            p.terminate()
            
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query to improve speech recognition accuracy and search relevance"""
        # Normalize common speech recognition errors
        speech_fixes = {
            'he to': 'need to',
            'you to': 'need to',
            'got a': 'have a',
            'packing the womb': 'uterine packing',
            'packing womb': 'uterine packing',
            'packing': 'wound packing',
            'womb': 'uterus',
            'uterus': 'uterine',
            'bleeding badly': 'severe bleeding',
            'bleeding bad': 'severe bleeding',
            'what about': '',
            'what other': 'additional',
            'other medication': 'additional medications',
            'other meds': 'additional medications',
            'should i give': 'administer',
            'need to give': 'administer',
            'want to give': 'administer',
            'going to give': 'administer',
            'patient': '',
            'patients': '',
            'my patient': '',
            'my patients': '',
            'the patient': '',
            'the patients': '',
            'kilograms': 'kg',
            'kilos': 'kg',
            'kgs': 'kg',
            'milligrams': 'mg',
            'mgs': 'mg',
            'micrograms': 'mcg',
            'mcgs': 'mcg',
            'grams': 'g',
            'gs': 'g',
            'milliliters': 'ml',
            'mls': 'ml',
            'units': 'units',
            'unit': 'unit',
            'cs symptoms': 'acs symptoms',
            'cs': 'acs',
            'a cs': 'acs',
            'having a cs': 'having acs',
            'acute cs': 'acute coronary syndrome',
            'coronary cs': 'coronary syndrome'
        }
        
        # Apply speech fixes
        processed_query = query.lower()
        
        # Special handling for CS -> ACS conversion
        if 'cs' in processed_query and 'acs' not in processed_query:
            # Check if it's likely ACS context
            acs_indicators = ['symptoms', 'patient', 'having', 'acute', 'coronary', 'heart', 'chest', 'pain']
            if any(indicator in processed_query for indicator in acs_indicators):
                processed_query = processed_query.replace('cs', 'acs')
        
        # Apply other speech fixes
        for speech_error, correction in speech_fixes.items():
            processed_query = processed_query.replace(speech_error, correction)
        
        # Add medical context keywords
        medical_context = {
            'bleeding': ['hemorrhage', 'blood loss', 'hemostatic'],
            'wound': ['laceration', 'injury', 'trauma'],
            'pain': ['analgesia', 'analgesic', 'pain management'],
            'airway': ['intubation', 'ventilation', 'breathing'],
            'shock': ['hypotension', 'hypovolemia', 'resuscitation'],
            'fracture': ['bone', 'orthopedic', 'splint'],
            'burn': ['thermal', 'chemical', 'debridement'],
            'chest': ['thoracic', 'pneumothorax', 'chest tube'],
            'abdomen': ['abdominal', 'laparotomy', 'surgery'],
            'head': ['neurological', 'brain', 'tbi'],
            'obstetric': ['pregnancy', 'delivery', 'uterine'],
            'gynecological': ['uterine', 'vaginal', 'pelvic']
        }
        
        # Add context keywords if medical terms are detected
        for term, context_terms in medical_context.items():
            if term in processed_query:
                processed_query += ' ' + ' '.join(context_terms[:2])  # Add top 2 context terms
        
        return processed_query.strip()

    def _enhance_search_query(self, query: str) -> str:
        """Enhance search query with medical synonyms and related terms"""
        # Medical synonyms mapping
        medical_synonyms = {
            'ketamine': 'ketamine analgesia sedation',
            'morphine': 'morphine analgesia pain',
            'fentanyl': 'fentanyl analgesia pain',
            'txa': 'tranexamic acid hemorrhage',
            'tranexamic': 'tranexamic acid hemorrhage',
            'epinephrine': 'epinephrine cardiac arrest',
            'atropine': 'atropine bradycardia',
            'blood': 'blood transfusion hemorrhage',
            'transfusion': 'blood transfusion whole blood',
            'whole blood': 'blood transfusion whole blood packed red',
            'packed red': 'packed red blood cells transfusion',
            'prbc': 'packed red blood cells transfusion',
            'bleeding': 'hemorrhage bleeding control',
            'hemorrhage': 'hemorrhage bleeding control',
            'airway': 'airway management intubation',
            'intubation': 'airway management intubation',
            'chest tube': 'thoracostomy chest tube',
            'thoracotomy': 'emergency thoracotomy',
            'tourniquet': 'tourniquet hemorrhage control',
            'pressure': 'pressure dressing hemorrhage',
            'packing': 'wound packing hemorrhage',
            'uterine': 'uterine hemorrhage obstetric',
            'womb': 'uterine hemorrhage obstetric',
            'obstetric': 'obstetric hemorrhage pregnancy',
            'pregnancy': 'obstetric hemorrhage pregnancy',
            'delivery': 'obstetric delivery pregnancy',
            'fracture': 'fracture orthopedic splint',
            'burn': 'burn management thermal',
            'shock': 'shock resuscitation hypotension',
            'cardiac': 'cardiac arrest resuscitation',
            'arrest': 'cardiac arrest resuscitation',
            'cpr': 'cardiac arrest resuscitation',
            'seizure': 'seizure management anticonvulsant',
            'infection': 'infection antibiotic sepsis',
            'sepsis': 'sepsis infection antibiotic',
            'acs': 'acute coronary syndrome myocardial infarction',
            'acute coronary': 'acute coronary syndrome myocardial infarction',
            'chest pain': 'acute coronary syndrome myocardial infarction',
            'heart attack': 'myocardial infarction acute coronary syndrome',
            'mi': 'myocardial infarction acute coronary syndrome',
            'pelvis': 'pelvic fracture trauma orthopedic',
            'pelvic': 'pelvic fracture trauma orthopedic',
            'fracture': 'orthopedic trauma bone extremity',
            'trauma': 'trauma orthopedic fracture extremity',
            'amputation': 'amputation trauma extremity hemorrhage'
        }
        
        # Apply synonyms
        enhanced_query = query.lower()
        for term, synonyms in medical_synonyms.items():
            if term in enhanced_query:
                enhanced_query += ' ' + synonyms
        
        return enhanced_query

    def search_corpus(self, query: str, top_n: int = 5) -> List[Dict]:
        """Enhanced search with query preprocessing and medical context"""
        if not self.bm25:
            raise RuntimeError("BM25 index not built")
        
        # Preprocess the query
        processed_query = self._preprocess_query(query)
        
        # Enhance with medical synonyms
        enhanced_query = self._enhance_search_query(processed_query)
        
        # Clean and normalize query
        query = enhanced_query.lower().strip()
        
        # Tokenize query
        query_tokens = query.split()
        
        # Get top n results using rank_bm25
        results = self.bm25.get_top_n(query_tokens, self.corpus, n=top_n)
        
        # Apply content density ranking
        results = self._rank_by_content_density(results, query)
        
        # If no good results, try keyword search
        if not results or len(results) == 0:
            results = self._keyword_search(query, top_n)
        
        return results
    
    def _rank_by_content_density(self, results: List[Dict], query: str) -> List[Dict]:
        """Rank results by content density (treatment vs. headers)"""
        scored_results = []
        
        for result in results:
            text = result['text'].lower()
            score = 0
            
            # Boost for dosage units
            if re.search(r'\d+\s*(?:mg|mcg|g|ml|kg)', text):
                score += 3
            
            # Boost for medication names
            med_names = ['ketamine', 'morphine', 'fentanyl', 'txa', 'tranexamic', 'epinephrine', 'atropine']
            for med in med_names:
                if med in text:
                    score += 2
            
            # Boost for action verbs
            action_verbs = ['give', 'administer', 'apply', 'insert', 'perform', 'monitor', 'check']
            for verb in action_verbs:
                if verb in text:
                    score += 1
            
            # Penalize for header-like content
            header_indicators = ['introduction', 'background', 'contributors', 'publication date']
            for indicator in header_indicators:
                if indicator in text:
                    score -= 2
            
            # Penalize for very short content
            if len(text) < 50:
                score -= 3
            
            scored_results.append((score, result))
        
        # Sort by score and return
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for score, result in scored_results]
    
    def _keyword_search(self, query: str, top_n: int) -> List[Dict]:
        """Fallback keyword search for medical queries"""
        query_words = query.lower().split()
        scored_results = []
        
        for entry in self.corpus:
            text = entry['text'].lower()
            source = entry['source'].lower()
            section = entry.get('section', '').lower()
            
            # Calculate relevance score
            score = 0
            
            # Check for exact word matches
            for word in query_words:
                if word in text:
                    score += 2
                if word in source:
                    score += 3
                if word in section:
                    score += 1
            
            # Check for medical term variations
            medical_terms = {
                'tbi': ['brain', 'traumatic', 'injury'],
                'ventilator': ['mechanical', 'ventilation', 'respiratory'],
                'trauma': ['traumatic', 'injury', 'emergency'],
                'anesthesia': ['anesthetic', 'sedation', 'intubation']
            }
            
            for term, variations in medical_terms.items():
                if term in query_words:
                    for var in variations:
                        if var in text or var in source:
                            score += 2
            
            if score > 0:
                scored_results.append((score, entry))
        
        # Sort by score and return top results
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in scored_results[:top_n]]
        
    def process_query(self, query):
        """Enhanced medical decision support: User speaks → STT → text → Update context OR request → BM25 search → Check contraindications → Speak response"""
        start_time = time.time()
        
        # Clean and normalize query
        query = query.lower().strip()
        
        # Update patient context or process medical request
        context_updated = self._update_patient_context(query)
        
        if context_updated:
            # Context was updated, acknowledge and ask for next request
            response = self._acknowledge_context_update(query)
        else:
            # Process medical request
            response = self._process_medical_request(query)
        
        # Add to conversation history
        self.conversation_history.append({
            'query': query,
            'response': response,
            'timestamp': time.time()
        })
        
        response_time = time.time() - start_time
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📋 Response: {response}")
        
        return response
    
    def _update_patient_context(self, query):
        """Update patient context based on voice input"""
        updated = False
        
        # Extract weight
        weight_match = re.search(r'(\d+)\s*(?:kg|kilo|pound|lb|kilogram)', query)
        if weight_match:
            weight_value = int(weight_match.group(1))
            if any(unit in query for unit in ['pound', 'lb']):
                self.patient_context['weight'] = weight_value * 0.453592
            else:
                self.patient_context['weight'] = weight_value
            updated = True
        else:
            # Try to find numbers that might be weights (common speech patterns)
            number_match = re.search(r'(\d+)\s*(?:kilo|kilogram|kg)', query)
            if number_match:
                self.patient_context['weight'] = int(number_match.group(1))
                updated = True
        
        # Extract allergies
        if 'allergic' in query or 'allergy' in query:
            allergy_terms = ['penicillin', 'sulfa', 'aspirin', 'latex', 'peanuts', 'shellfish']
            for term in allergy_terms:
                if term in query and term not in self.patient_context['allergies']:
                    self.patient_context['allergies'].append(term)
                    updated = True
        
        # Extract conditions
        conditions = {
            'pregnancy': ['pregnant', 'pregnancy'],
            'diabetes': ['diabetic', 'diabetes'],
            'hypertension': ['hypertension', 'high blood pressure'],
            'asthma': ['asthma', 'asthmatic'],
            'heart_disease': ['heart disease', 'cardiac disease', 'mi', 'heart attack', 'myocardial infarction', 'coronary artery disease', 'cardiovascular disease']
        }
        
        for condition, keywords in conditions.items():
            for keyword in keywords:
                # Use word boundary matching to avoid false positives
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, query, re.IGNORECASE) and condition not in self.patient_context['conditions']:
                    self.patient_context['conditions'].append(condition)
                    updated = True
                    break
        
        # Extract vitals
        vitals_patterns = {
            'bp': r'(\d+)/(\d+)',
            'hr': r'hr\s*(\d+)',
            'temp': r'temp\s*(\d+(?:\.\d+)?)',
            'spo2': r'spo2\s*(\d+)',
            'rr': r'rr\s*(\d+)'
        }
        
        for vital, pattern in vitals_patterns.items():
            match = re.search(pattern, query)
            if match:
                current_time = time.time()
                
                if vital == 'bp':
                    systolic = int(match.group(1))
                    diastolic = int(match.group(2))
                    self.patient_context['vitals']['systolic'] = systolic
                    self.patient_context['vitals']['diastolic'] = diastolic
                    
                    # Store in history
                    self.patient_context['vital_history'].append({
                        'timestamp': current_time,
                        'vital': 'bp',
                        'value': f"{systolic}/{diastolic}"
                    })
                else:
                    value = float(match.group(1))
                    self.patient_context['vitals'][vital] = value
                    
                    # Store in history
                    self.patient_context['vital_history'].append({
                        'timestamp': current_time,
                        'vital': vital,
                        'value': value
                    })
                
                self.patient_context['last_vital_check'] = current_time
                updated = True
        
        return updated
    
    def _check_vital_timing(self) -> str:
        """Check if vitals need to be updated based on timing"""
        current_time = time.time()
        last_check = self.patient_context.get('last_vital_check')
        
        if not last_check:
            return "No vitals recorded. Please provide current vitals."
        
        time_since_check = current_time - last_check
        minutes_since_check = time_since_check / 60
        
        # Check if critical patient needs frequent vitals
        if self.patient_context.get('critical_patient', False):
            if minutes_since_check > 5:  # Critical patients every 5 minutes
                return f"Critical patient - vitals needed. Last check: {minutes_since_check:.0f} minutes ago."
        else:
            if minutes_since_check > 15:  # Regular patients every 15 minutes
                return f"Vitals may be outdated. Last check: {minutes_since_check:.0f} minutes ago."
        
        return None
    
    def _get_vital_summary(self) -> str:
        """Get a summary of current vitals"""
        if not self.patient_context['vitals']:
            return "No vitals recorded."
        
        vitals = self.patient_context['vitals']
        summary_parts = []
        
        if 'systolic' in vitals and 'diastolic' in vitals:
            summary_parts.append(f"BP: {vitals['systolic']}/{vitals['diastolic']}")
        
        if 'hr' in vitals:
            summary_parts.append(f"HR: {vitals['hr']}")
        
        if 'spo2' in vitals:
            summary_parts.append(f"SpO2: {vitals['spo2']}%")
        
        if 'rr' in vitals:
            summary_parts.append(f"RR: {vitals['rr']}")
        
        if 'temp' in vitals:
            summary_parts.append(f"Temp: {vitals['temp']}°C")
        
        return ", ".join(summary_parts)
    
    def _acknowledge_context_update(self, query):
        """Acknowledge context update and provide summary"""
        if self.patient_context['weight']:
            return f"Patient context updated. Weight: {self.patient_context['weight']:.1f} kg. What medical assistance do you need?"
        elif self.patient_context['allergies']:
            return f"Allergies noted: {', '.join(self.patient_context['allergies'])}. What medical assistance do you need?"
        elif self.patient_context['conditions']:
            return f"Conditions noted: {', '.join(self.patient_context['conditions'])}. What medical assistance do you need?"
        elif self.patient_context['vitals']:
            vitals_str = ', '.join([f"{k}: {v}" for k, v in self.patient_context['vitals'].items()])
            return f"Vitals recorded: {vitals_str}. What medical assistance do you need?"
        else:
            return "Context updated. What medical assistance do you need?"
    
    def _process_medical_request(self, query):
        """Process medical request with intelligent query understanding and vital signs analysis"""
        
        query_lower = query.lower()
        
        # Check vital timing first
        vital_timing_warning = self._check_vital_timing()
        if vital_timing_warning:
            return vital_timing_warning
        
        # Analyze current vitals if available
        if self.patient_context['vitals']:
            vital_assessment = self.vital_analyzer.get_treatment_recommendation(
                self.patient_context['vitals'], 
                query
            )
            
            # If critical vitals, prioritize stabilization
            if vital_assessment.startswith("CRITICAL:"):
                return vital_assessment
        
        # Direct medication queries - give immediate answers with vital consideration
        if 'ketamine' in query_lower:
            if 'pain' in query_lower:
                return self._get_ketamine_pain_dose()
            elif 'sedation' in query_lower:
                return self._get_ketamine_sedation_dose()
            else:
                return self._get_ketamine_dose()
        
        if 'morphine' in query_lower:
            return self._get_morphine_dose()
        
        if 'fentanyl' in query_lower:
            return self._get_fentanyl_dose()
        
        if 'txa' in query_lower or 'tranexamic' in query_lower:
            return self._get_txa_dose()
        
        if 'epinephrine' in query_lower or 'epi' in query_lower:
            if 'arrest' in query_lower:
                return "Epinephrine 1mg IV every 3-5 minutes."
            elif 'anaphylaxis' in query_lower:
                return "Epinephrine 0.3-0.5mg IM every 5-15 minutes."
            else:
                return "Epinephrine 1mg IV for cardiac arrest, 0.3-0.5mg IM for anaphylaxis."
        
        if 'atropine' in query_lower:
            return "Atropine 1mg IV. May repeat every 3-5 minutes up to 3mg total."
        
        # Direct procedure queries
        if 'bleeding' in query_lower or 'hemorrhage' in query_lower:
            if 'arterial' in query_lower:
                return "Apply direct pressure and tourniquet if needed. Reassess every 10 minutes."
            elif 'severe' in query_lower:
                return "Apply tourniquet above wound. Reassess in 2 hours."
            else:
                return "Apply direct pressure and hemostatic dressing. Reassess every 10 minutes."
        
        if 'airway' in query_lower:
            if 'obstruction' in query_lower:
                return "Insert NPA if unconscious. If ineffective: surgical cricothyrotomy."
            elif 'intubation' in query_lower:
                return "Rapid sequence intubation: Ketamine 1-2 mg/kg IV, Rocuronium 0.6-1.2 mg/kg IV."
            else:
                return "Assess for obstruction. Insert NPA if unconscious. If ineffective: surgical cricothyrotomy."
        
        if 'pneumothorax' in query_lower:
            if 'tension' in query_lower:
                return "Needle decompression 2nd intercostal space, mid-clavicular line."
            elif 'open' in query_lower:
                return "Apply occlusive dressing taped on 3 sides. Monitor respiratory status."
            else:
                return "Needle decompression 2nd intercostal space for tension pneumothorax."
        
        if 'chest pain' in query_lower or 'acs' in query_lower:
            if 'acs' in query_lower or 'acute coronary' in query_lower:
                return "Aspirin 325mg PO, Nitroglycerin 0.4mg SL q5min x3, 12-lead ECG immediately."
            else:
                return "Aspirin 325mg PO, Nitroglycerin 0.4mg SL q5min x3, 12-lead ECG."
        
        if 'fracture' in query_lower:
            if 'pelvis' in query_lower or 'pelvic' in query_lower:
                return "Apply pelvic binder if unstable. Control hemorrhage. Monitor for shock."
            else:
                return "Immobilize fracture. Assess neurovascular status. Apply splint."
        
        if 'burn' in query_lower:
            if 'chemical' in query_lower:
                return "Flush with copious water. Remove contaminated clothing. Monitor airway."
            else:
                return "Cool with room temperature water. Cover with sterile dressing. Monitor airway."
        
        # Handle vital signs queries
        if any(term in query_lower for term in ['vitals', 'vital signs', 'current vitals', 'patient status']):
            return self._get_vital_summary()
        
        # Handle critical patient designation
        if 'critical' in query_lower or 'unstable' in query_lower:
            self.patient_context['critical_patient'] = True
            return "Patient marked as critical. Vitals will be checked every 5 minutes."
        
        # If no direct match, ask for clarification
        return "I need more context. What specific medical assistance do you need?"
    
    def _get_ketamine_pain_dose(self):
        """Get ketamine dose for pain"""
        if self.patient_context['weight']:
            dose = 0.3 * self.patient_context['weight']
            return f"Ketamine 0.3 mg/kg IV. For {self.patient_context['weight']:.0f}kg patient: {dose:.0f}mg IV."
        else:
            return "Ketamine 0.3 mg/kg IV for pain. Monitor respiratory rate."
    
    def _get_ketamine_sedation_dose(self):
        """Get ketamine dose for sedation"""
        if self.patient_context['weight']:
            dose = 1.5 * self.patient_context['weight']  # Use 1.5 mg/kg for sedation
            return f"Ketamine 1.5 mg/kg IV. For {self.patient_context['weight']:.0f}kg patient: {dose:.0f}mg IV."
        else:
            return "Ketamine 1-2 mg/kg IV for sedation. Monitor respiratory rate."
    
    def _get_ketamine_dose(self):
        """Get general ketamine dose"""
        if self.patient_context['weight']:
            dose = 0.3 * self.patient_context['weight']
            return f"Ketamine 0.3 mg/kg IV for pain, 1-2 mg/kg IV for sedation. For {self.patient_context['weight']:.0f}kg patient: {dose:.0f}mg IV for pain."
        else:
            return "Ketamine 0.3 mg/kg IV for pain, 1-2 mg/kg IV for sedation."
    
    def _get_morphine_dose(self):
        """Get morphine dose"""
        if self.patient_context['weight']:
            dose = 0.1 * self.patient_context['weight']
            return f"Morphine 0.1 mg/kg IV. For {self.patient_context['weight']:.0f}kg patient: {dose:.0f}mg IV."
        else:
            return "Morphine 0.1 mg/kg IV. Monitor respiratory rate."
    
    def _get_fentanyl_dose(self):
        """Get fentanyl dose"""
        if self.patient_context['weight']:
            dose = 1.0 * self.patient_context['weight']
            return f"Fentanyl 1 mcg/kg IV. For {self.patient_context['weight']:.0f}kg patient: {dose:.0f}mcg IV."
        else:
            return "Fentanyl 1 mcg/kg IV. Monitor for respiratory depression."
    
    def _get_txa_dose(self):
        """Get TXA dose"""
        return "TXA 1g IV over 10 minutes. Then 1g over 8 hours."
    

    
    def _check_contraindications(self, query, response):
        """Check for general contraindications"""
        warnings = []
        
        # Check for pregnancy contraindications
        if 'pregnancy' in self.patient_context['conditions']:
            if any(drug in query for drug in ['ketamine', 'morphine', 'fentanyl']):
                warnings.append("Pregnancy may affect drug metabolism")
        
        # Check for hypertension contraindications
        if 'hypertension' in self.patient_context['conditions']:
            if 'epinephrine' in query:
                warnings.append("Epinephrine may exacerbate hypertension")
        
        # Check for asthma contraindications
        if 'asthma' in self.patient_context['conditions']:
            if 'aspirin' in query or 'nsaids' in query:
                warnings.append("NSAIDs may trigger asthma exacerbation")
        
        return '; '.join(warnings) if warnings else None
    

    

    
    def _extract_treatment_from_paragraph(self, text, query, source):
        """Extract actionable treatment information from JTS paragraph"""
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Check for medication names and extract dosages
        medications = {
            'ketamine': {'pattern': r'(\d+(?:\.\d+)?)\s*mg/kg', 'default_dose': 0.3, 'route': 'IV'},
            'morphine': {'pattern': r'(\d+(?:\.\d+)?)\s*mg/kg', 'default_dose': 0.1, 'route': 'IV'},
            'fentanyl': {'pattern': r'(\d+(?:\.\d+)?)\s*mcg/kg', 'default_dose': 1.0, 'route': 'IV'},
            'txa': {'pattern': r'(\d+)\s*(?:mg|g)', 'default_dose': 1000, 'route': 'IV'},
            'tranexamic': {'pattern': r'(\d+)\s*(?:mg|g)', 'default_dose': 1000, 'route': 'IV'},
            'epinephrine': {'pattern': r'(\d+(?:\.\d+)?)\s*mg', 'default_dose': 1.0, 'route': 'IV'},
            'atropine': {'pattern': r'(\d+(?:\.\d+)?)\s*mg', 'default_dose': 1.0, 'route': 'IV'}
        }
        
        # Check for specific medications in query and text
        for med_name, med_info in medications.items():
            if med_name in query.lower() and med_name in text.lower():
                # Extract dosage from text if available
                dose_match = re.search(med_info['pattern'], text, re.IGNORECASE)
                if dose_match:
                    extracted_dose = float(dose_match.group(1))
                    if self.patient_context['weight']:
                        if 'mg/kg' in med_info['pattern'] or 'mcg/kg' in med_info['pattern']:
                            total_dose = extracted_dose * self.patient_context['weight']
                            unit = 'mg' if 'mg/kg' in med_info['pattern'] else 'mcg'
                            return f"{med_name.title()}: {extracted_dose} {unit}/kg {med_info['route']}. For {self.patient_context['weight']:.0f} kg: {total_dose:.0f} {unit}."
                        else:
                            return f"{med_name.title()}: {extracted_dose} {med_info['route']}."
                    else:
                        return f"{med_name.title()}: {extracted_dose} {med_info['route']}."
                else:
                    # Use default dose if not found in text
                    if self.patient_context['weight']:
                        if 'mg/kg' in med_info['pattern'] or 'mcg/kg' in med_info['pattern']:
                            total_dose = med_info['default_dose'] * self.patient_context['weight']
                            unit = 'mg' if 'mg/kg' in med_info['pattern'] else 'mcg'
                            return f"{med_name.title()}: {med_info['default_dose']} {unit}/kg {med_info['route']}. For {self.patient_context['weight']:.0f} kg: {total_dose:.0f} {unit}."
                        else:
                            return f"{med_name.title()}: {med_info['default_dose']} {med_info['route']}."
                    else:
                        return f"{med_name.title()}: {med_info['default_dose']} {med_info['route']}."
        
        # Extract action verbs and procedures
        action_patterns = {
            'tourniquet': r'(?:apply|place|use)\s+tourniquet',
            'pressure': r'(?:apply|direct)\s+pressure',
            'airway': r'(?:insert|place)\s+(?:NPA|airway)',
            'cricothyrotomy': r'(?:perform|surgical)\s+cricothyrotomy',
            'monitor': r'(?:monitor|check)\s+(?:BP|HR|RR|vitals)'
        }
        
        for action, pattern in action_patterns.items():
            if action in query.lower():
                # Check if action is mentioned in text
                if re.search(pattern, text, re.IGNORECASE):
                    action_match = re.search(pattern, text, re.IGNORECASE)
                    if action_match:
                        return f"Action: {action_match.group(0)}"
                else:
                    # Return standard protocol if not found in text
                    if action == 'tourniquet':
                        return "Apply tourniquet above wound. Reassess in 2 hours."
                    elif action == 'pressure':
                        return "Apply direct pressure and hemostatic dressing. Reassess every 10 minutes."
                    elif action == 'airway':
                        return "Assess for obstruction. Insert NPA if unconscious. If ineffective: surgical cricothyrotomy."
        
        # If no specific treatment found, return cleaned text
        return self._clean_and_summarize_text(text)
    
    def _clean_and_summarize_text(self, text):
        """Clean and summarize JTS text for voice output"""
        
        # Remove common headers and non-actionable content
        text = re.sub(r'JOINT TRAUMA SYS TEM CLINICAL PRACTICE GUIDELINE.*?Contributors.*?', '', text)
        text = re.sub(r'This CPG.*?guidance.*?', '', text)
        text = re.sub(r'Publication Date.*?', '', text)
        text = re.sub(r'CONTRIBUTORS.*?', '', text)
        
        # Limit length for voice output
        if len(text) > 300:
            sentences = text.split('.')
            if len(sentences) > 1:
                text = '. '.join(sentences[:2]) + '.'
            else:
                text = text[:300] + "..."
        
        return text.strip()
        
    def voice_interaction_loop(self) -> None:
        """Main voice interaction loop with Crusu protocol support"""
        print("🎤 JTS Recall Engine - Voice Interface")
        print("=====================================")
        print("Speak medical queries clearly into your microphone")
        print("Examples:")
        print("- 'how do I stop arterial bleeding'")
        print("- 'what is the treatment for open pneumothorax'")
        print("- 'ketamine dosage for pain'")
        print("")
        
        # Test voice
        speak("JTS Recall Engine ready. Speak your medical query.")
        
        while True:
            try:
                # Listen for query
                query = self.listen_for_query()
                
                if not query:
                    print("❌ No speech detected. Please try again.")
                    continue
                    
                print(f"🎤 Query: {query}")
                
                # Process query
                start_time = time.time()
                response = self.process_query(query)
                end_time = time.time()
                
                print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
                print(f"📋 Response: {response[:200]}...")
                
                # Speak response
                speak(response)
                
                # Handle clarifying questions for bleeding
                if response == "Is the bleeding minor, moderate, or severe?":
                    print("🎤 Listening for bleeding severity...")
                    severity_query = self.listen_for_query()
                    
                    if severity_query:
                        print(f"🎤 Severity: {severity_query}")
                        
                        # Process severity response
                        if 'severe' in severity_query.lower():
                            final_response = "Apply tourniquet above wound. Reassess in 2 hours."
                        elif 'moderate' in severity_query.lower():
                            final_response = "Apply direct pressure and hemostatic dressing. Reassess every 10 minutes."
                        elif 'minor' in severity_query.lower():
                            final_response = "Apply direct pressure for 10 minutes. Monitor for continued bleeding."
                        else:
                            final_response = "Apply direct pressure and hemostatic dressing. Reassess every 10 minutes."
                        
                        speak(final_response)
                
                print("")
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping JTS Recall Engine...")
                speak("JTS Recall Engine stopped.")
                break
            except Exception as e:
                logger.error(f"Error in voice interaction: {e}")
                speak("Sorry, there was an error processing your query. Please try again.")

def main():
    """Main function to run JTS Recall Engine"""
    engine = JTSRecallEngine()
    
    try:
        engine.initialize()
        engine.voice_interaction_loop()
    except Exception as e:
        logger.error(f"Error initializing JTS Recall Engine: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 