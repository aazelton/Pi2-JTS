#!/usr/bin/env python3
"""
JTS Clinical Decision Engine
Voice-driven clinical decision making using Joint Trauma Services guidelines
Optimized for Pi2 with efficient search and retrieval
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from difflib import get_close_matches

# Add system Python packages to path for PyPDF2
sys.path.append('/Users/andrew/Library/Python/3.9/lib/python/site-packages')

logger = logging.getLogger(__name__)

class JTSDecisionEngine:
    def __init__(self, data_directory: str = "jts_data"):
        self.data_directory = Path(data_directory)
        self.guidelines = {}
        self.metadata = {}
        self.load_guidelines()
        
        # Clinical decision patterns
        self.decision_patterns = {
            "assessment": ["assess", "evaluate", "examine", "check", "look for"],
            "intervention": ["treat", "intervene", "manage", "administer", "apply"],
            "monitoring": ["monitor", "observe", "watch", "track", "follow"],
            "emergency": ["emergency", "urgent", "immediate", "critical", "stat"],
            "medication": ["medication", "drug", "dose", "administer", "give"]
        }
    
    def load_guidelines(self):
        """Load processed JTS guidelines"""
        if not self.data_directory.exists():
            logger.warning(f"JTS data directory {self.data_directory} not found")
            return
        
        # Load metadata
        metadata_file = self.data_directory / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
        
        # Load guidelines by category
        for category_file in self.data_directory.glob("*_guidelines.json"):
            category = category_file.stem.replace("_guidelines", "")
            with open(category_file, 'r', encoding='utf-8') as f:
                self.guidelines[category] = json.load(f)
        
        logger.info(f"Loaded {len(self.guidelines)} categories of guidelines")
    
    def search_guidelines(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search guidelines for relevant information"""
        query_lower = query.lower()
        results = []
        
        # Extract key terms for broader search
        search_terms = []
        if 'ketamine' in query_lower:
            search_terms.extend(['ketamine', 'pain', 'analgesia', 'sedation'])
        if 'burn' in query_lower:
            search_terms.extend(['burn', 'burned', 'burning'])
        if 'airway' in query_lower:
            search_terms.extend(['airway', 'intubation', 'ventilation'])
        if 'hemorrhage' in query_lower or 'shock' in query_lower:
            search_terms.extend(['hemorrhage', 'shock', 'resuscitation', 'circulation'])
        if 'trauma' in query_lower:
            search_terms.extend(['trauma', 'injury'])
        
        # If no specific terms, use original query
        if not search_terms:
            search_terms = [query_lower]
        
        # Determine relevant categories
        search_categories = [category] if category else list(self.guidelines.keys())
        
        for cat in search_categories:
            if cat not in self.guidelines:
                continue
            
            for filename, content in self.guidelines[cat].items():
                relevance_score = 0
                matched_sections = []
                
                # Search for each term
                for term in search_terms:
                    # Search in sections
                    for section_name, section_content in content.get('sections', {}).items():
                        if term in section_content.lower():
                            relevance_score += 2
                            matched_sections.append(section_name)
                    
                    # Search in full text
                    if term in content.get('full_text', '').lower():
                        relevance_score += 1
                    
                    # Search in filename
                    if term in filename.lower():
                        relevance_score += 3
                
                if relevance_score > 0:
                    results.append({
                        'filename': filename,
                        'category': cat,
                        'relevance_score': relevance_score,
                        'matched_sections': matched_sections,
                        'content': content
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:5]  # Return top 5 results
    
    def extract_clinical_decision(self, query: str) -> Dict:
        """Extract clinical decision from voice query"""
        query_lower = query.lower()
        
        # Extract patient parameters (weight, age, etc.)
        patient_params = self.extract_patient_parameters(query)
        
        # Determine decision type
        decision_type = "general"
        for pattern_type, keywords in self.decision_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                decision_type = pattern_type
                break
        
        # Search for relevant guidelines
        results = self.search_guidelines(query)
        
        # Generate actionable recommendations
        recommendations = []
        for result in results[:3]:  # Top 3 results
            content = result['content']
            
            # Extract specific clinical actions and dosages
            clinical_actions = self.extract_clinical_actions(content, query, patient_params)
            
            recommendations.append({
                'source': result['filename'],
                'category': result['category'],
                'actions': clinical_actions,
                'relevance_score': result['relevance_score']
            })
        
        return {
            'query': query,
            'decision_type': decision_type,
            'patient_params': patient_params,
            'relevant_guidelines': results,
            'recommendations': recommendations,
            'confidence': len(results) > 0
        }
    
    def extract_patient_parameters(self, query: str) -> Dict:
        """Extract patient parameters from query"""
        import re
        
        params = {}
        
        # Extract weight
        weight_match = re.search(r'(\d+)\s*(?:kg|kilos?|pounds?|lbs?)', query.lower())
        if weight_match:
            weight = int(weight_match.group(1))
            # Convert pounds to kg if needed
            if any(unit in query.lower() for unit in ['pound', 'lbs', 'lb']):
                weight = weight * 0.453592
            params['weight_kg'] = weight
        
        # Extract age
        age_match = re.search(r'(\d+)\s*(?:years?|y\.?o\.?|yo)', query.lower())
        if age_match:
            params['age_years'] = int(age_match.group(1))
        
        # Extract other parameters
        if 'burn' in query.lower():
            params['condition'] = 'burn'
        if 'trauma' in query.lower():
            params['condition'] = 'trauma'
        if 'pain' in query.lower():
            params['symptom'] = 'pain'
        
        return params
    
    def extract_clinical_actions(self, content: Dict, query: str, patient_params: Dict) -> List[Dict]:
        """Extract specific clinical actions and dosages"""
        actions = []
        text = content.get('full_text', '').lower()
        query_lower = query.lower()
        
        # Look for medication dosages
        if any(med in query_lower for med in ['ketamine', 'morphine', 'fentanyl', 'midazolam']):
            med_actions = self.extract_medication_dosages(text, query, patient_params)
            actions.extend(med_actions)
        
        # Look for procedural steps
        if any(proc in query_lower for proc in ['airway', 'intubation', 'cpr', 'resuscitation']):
            proc_actions = self.extract_procedural_steps(text, query)
            actions.extend(proc_actions)
        
        # Look for assessment criteria
        if any(assess in query_lower for assess in ['assess', 'evaluate', 'check', 'examine']):
            assess_actions = self.extract_assessment_criteria(text, query)
            actions.extend(assess_actions)
        
        # For airway queries, prioritize decision trees over guideline extraction
        if 'airway' in query_lower:
            tree_actions = self.apply_clinical_decision_trees(query_lower, patient_params)
            if tree_actions:
                actions = tree_actions  # Replace any guideline results with decision tree
        else:
            # If no specific actions found, try clinical decision trees
            if not actions:
                tree_actions = self.apply_clinical_decision_trees(query_lower, patient_params)
                actions.extend(tree_actions)
        
        return actions
    
    def apply_clinical_decision_trees(self, query: str, patient_params: Dict) -> List[Dict]:
        """Apply clinical decision trees for common scenarios"""
        actions = []
        
        # Airway decision tree
        if 'airway' in query:
            if 'compromise' in query or 'obstruction' in query:
                actions.append({
                    'type': 'procedural_step',
                    'description': 'Assess airway patency. If obstructed, attempt basic adjuncts (NPA/OPA). If unsuccessful, prepare for RSI with ketamine.',
                    'priority': 'critical',
                    'priority_score': 5
                })
            elif 'intubation' in query:
                actions.append({
                    'type': 'procedural_step',
                    'description': 'Prepare for RSI: ketamine 1-2mg/kg IV, apply apneic oxygenation, have backup airway ready.',
                    'priority': 'critical',
                    'priority_score': 5
                })
            else:
                actions.append({
                    'type': 'procedural_step',
                    'description': 'Assess airway: look, listen, feel. Check for obstruction, stridor, or inability to speak.',
                    'priority': 'urgent',
                    'priority_score': 4
                })
        
        # Hemorrhage decision tree
        elif 'hemorrhage' in query or 'shock' in query:
            actions.append({
                'type': 'procedural_step',
                'description': 'Control bleeding with direct pressure. Start IV access. Consider tourniquet for extremity bleeding.',
                'priority': 'critical',
                'priority_score': 5
            })
        
        # Burn decision tree
        elif 'burn' in query:
            actions.append({
                'type': 'procedural_step',
                'description': 'Cool burn with room temperature water. Remove jewelry. Assess airway for inhalation injury.',
                'priority': 'urgent',
                'priority_score': 4
            })
        
        return actions
    
    def extract_medication_dosages(self, text: str, query: str, patient_params: Dict) -> List[Dict]:
        """Extract and calculate medication dosages"""
        actions = []
        
        # Ketamine dosing patterns
        if 'ketamine' in query.lower():
            # Look for ketamine dosage patterns in text
            import re
            
            # Common ketamine dosing patterns - more specific to avoid false positives
            patterns = [
                r'ketamine\s*\(?\s*(\d+(?:\.\d+)?)\s*mg/kg\s*\)?',
                r'(\d+(?:\.\d+)?)\s*mg/kg\s*ketamine',
                r'ketamine\s*(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*mg/kg',
                r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*mg/kg\s*ketamine'
            ]
            
            found_dosage = False
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        min_dose = float(match[0])
                        max_dose = float(match[1]) if len(match) > 1 else min_dose
                    else:
                        min_dose = max_dose = float(match)
                    
                    # Validate dosage ranges (reasonable ketamine dosing)
                    if min_dose < 0.1 or max_dose > 10.0:
                        continue  # Skip unreasonable dosages
                    
                    found_dosage = True
                    # Calculate actual dose if weight is provided
                    if 'weight_kg' in patient_params:
                        weight = patient_params['weight_kg']
                        actual_min = min_dose * weight
                        actual_max = max_dose * weight
                        
                        actions.append({
                            'type': 'medication_dosage',
                            'medication': 'ketamine',
                            'dose_range_mg_kg': f"{min_dose}-{max_dose}",
                            'calculated_dose_mg': f"{int(actual_min)}-{int(actual_max)}",
                            'patient_weight_kg': weight,
                            'route': 'IV/IM',
                            'frequency': 'as needed for pain',
                            'source': 'guideline'
                        })
                    else:
                        actions.append({
                            'type': 'medication_dosage',
                            'medication': 'ketamine',
                            'dose_range_mg_kg': f"{min_dose}-{max_dose}",
                            'note': 'Patient weight needed for exact calculation',
                            'source': 'guideline'
                        })
            
            # Fallback to standard dosing if no specific dosage found in guidelines
            if not found_dosage and 'weight_kg' in patient_params:
                weight = patient_params['weight_kg']
                
                # Standard ketamine dosing for pain management
                if 'burn' in query.lower() or 'pain' in query.lower():
                    # Pain management dosing
                    min_dose = 0.5  # mg/kg
                    max_dose = 1.0  # mg/kg
                    actual_min = min_dose * weight
                    actual_max = max_dose * weight
                    
                    actions.append({
                        'type': 'medication_dosage',
                        'medication': 'ketamine',
                        'dose_range_mg_kg': f"{min_dose}-{max_dose}",
                        'calculated_dose_mg': f"{int(actual_min)}-{int(actual_max)}",
                        'patient_weight_kg': weight,
                        'route': 'IV/IM',
                        'frequency': 'as needed for pain',
                        'source': 'standard_protocol',
                        'note': 'Standard pain management dosing'
                    })
                else:
                    # General anesthesia dosing
                    min_dose = 1.0  # mg/kg
                    max_dose = 2.0  # mg/kg
                    actual_min = min_dose * weight
                    actual_max = max_dose * weight
                    
                    actions.append({
                        'type': 'medication_dosage',
                        'medication': 'ketamine',
                        'dose_range_mg_kg': f"{min_dose}-{max_dose}",
                        'calculated_dose_mg': f"{int(actual_min)}-{int(actual_max)}",
                        'patient_weight_kg': weight,
                        'route': 'IV/IM',
                        'frequency': 'single dose',
                        'source': 'standard_protocol',
                        'note': 'Standard induction dosing'
                    })
        
        return actions
    
    def extract_procedural_steps(self, text: str, query: str) -> List[Dict]:
        """Extract procedural steps"""
        actions = []
        
        # Look for numbered steps or bullet points
        import re
        step_patterns = [
            r'(\d+)\.\s*([^.\n]+)',
            r'•\s*([^.\n]+)',
            r'-\s*([^.\n]+)'
        ]
        
        # Keywords that indicate critical steps
        critical_keywords = [
            'assess', 'check', 'evaluate', 'examine', 'look for',
            'intubate', 'ventilate', 'oxygenate', 'resuscitate',
            'control', 'stop', 'manage', 'treat', 'administer',
            'ketamine', 'morphine', 'fentanyl', 'midazolam'
        ]
        
        # Keywords to exclude (metadata, not actual steps)
        exclude_keywords = [
            'cpg', 'id:', 'guideline', 'document', 'permission',
            'adapted', 'transmit', 'photograph', 'algorithm'
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    step_num = match[0]
                    step_desc = match[1].strip()
                else:
                    step_desc = match.strip()
                
                # Skip if contains exclude keywords (metadata)
                step_lower = step_desc.lower()
                if any(exclude in step_lower for exclude in exclude_keywords):
                    continue
                
                # Calculate priority score
                priority_score = 0
                
                # Critical keywords get highest priority
                if any(keyword in step_lower for keyword in critical_keywords):
                    priority_score += 3
                
                # Emergency/urgent words
                if any(word in step_lower for word in ['emergency', 'urgent', 'immediate', 'critical']):
                    priority_score += 2
                
                # Airway-specific priority
                if 'airway' in query.lower() and any(word in step_lower for word in ['airway', 'intubate', 'ventilate']):
                    priority_score += 2
                
                # Medication-specific priority
                if any(med in query.lower() for med in ['ketamine', 'morphine', 'fentanyl']) and any(med in step_lower for med in ['ketamine', 'morphine', 'fentanyl']):
                    priority_score += 2
                
                actions.append({
                    'type': 'procedural_step',
                    'description': step_desc,
                    'priority_score': priority_score,
                    'priority': 'critical' if priority_score >= 3 else 'urgent' if priority_score >= 2 else 'standard'
                })
        
        # Sort by priority score and return only top 2-3
        actions.sort(key=lambda x: x['priority_score'], reverse=True)
        return actions[:3]  # Limit to top 3 most critical steps
    
    def extract_assessment_criteria(self, text: str, query: str) -> List[Dict]:
        """Extract assessment criteria"""
        actions = []
        
        # Look for assessment criteria
        import re
        criteria_patterns = [
            r'check\s+for\s+([^.\n]+)',
            r'assess\s+([^.\n]+)',
            r'evaluate\s+([^.\n]+)',
            r'look\s+for\s+([^.\n]+)'
        ]
        
        for pattern in criteria_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                actions.append({
                    'type': 'assessment_criteria',
                    'criteria': match.strip(),
                    'priority': 'critical' if any(word in match.lower() for word in ['airway', 'breathing', 'circulation']) else 'standard'
                })
        
        return actions[:3]  # Limit to top 3 criteria
    
    def generate_voice_response(self, decision: Dict) -> str:
        """Generate natural language response for voice output"""
        import re
        
        if not decision['confidence']:
            # Provide decision tree prompts for common scenarios
            query_lower = decision['query'].lower()
            if 'airway' in query_lower:
                return "I need more context. What would you like help with? Airway assessment, intubation, ventilation, or airway adjuncts?"
            elif 'circulation' in query_lower or 'shock' in query_lower:
                return "I need more context. What would you like help with? Hemorrhage control, resuscitation, blood products, or circulation assessment?"
            elif 'trauma' in query_lower:
                return "I need more context. What would you like help with? Trauma assessment, specific injury management, or trauma resuscitation?"
            else:
                return "I couldn't find specific guidelines for that query. Please try rephrasing or ask about a different aspect of trauma care."
        
        response_parts = []
        
        # Add specific clinical actions - limit to 1-2 key points
        if decision['recommendations']:
            seen_actions = set()  # Track seen actions to avoid duplicates
            action_count = 0
            max_actions = 2  # Limit to 2 key points
            
            for rec in decision['recommendations']:
                if rec.get('actions') and action_count < max_actions:
                    for action in rec['actions']:
                        if action_count >= max_actions:
                            break
                            
                        if action['type'] == 'medication_dosage':
                            if 'calculated_dose_mg' in action:
                                action_key = f"{action['medication']}_{action['calculated_dose_mg']}"
                                if action_key not in seen_actions:
                                    seen_actions.add(action_key)
                                    # Format dosage without decimals
                                    dose_range = action['calculated_dose_mg']
                                    if '-' in dose_range:
                                        min_dose, max_dose = dose_range.split('-')
                                        formatted_dose = f"{int(float(min_dose))}-{int(float(max_dose))}"
                                    else:
                                        formatted_dose = str(int(float(dose_range)))
                                    
                                    response_parts.append(f"{formatted_dose}mg {action['route']}")
                                    action_count += 1
                                    
                        elif action['type'] == 'procedural_step':
                            if action['priority'] in ['critical', 'urgent']:
                                # Clean up the description - remove extra spaces and shorten
                                desc = action['description'].strip()
                                # Remove common prefixes and clean up
                                desc = re.sub(r'^[•\-]\s*', '', desc)
                                desc = re.sub(r'\s+', ' ', desc)  # Remove extra spaces
                                
                                if len(desc) > 100:  # Truncate long descriptions
                                    desc = desc[:100] + "..."
                                
                                response_parts.append(desc)
                                action_count += 1
                                
                        elif action['type'] == 'assessment_criteria':
                            if action['priority'] == 'critical':
                                criteria = action['criteria'].strip()
                                if len(criteria) > 80:
                                    criteria = criteria[:80] + "..."
                                response_parts.append(f"Check {criteria}")
                                action_count += 1
        
        # If no specific actions found, provide very brief guidance
        if not response_parts:
            response_parts.append("Consult JTS guidelines for specific protocols.")
        
        return ". ".join(response_parts) + "."
    
    def get_available_categories(self) -> List[str]:
        """Get list of available guideline categories"""
        return list(self.guidelines.keys())
    
    def get_category_summary(self, category: str) -> Dict:
        """Get summary of guidelines in a category"""
        if category not in self.guidelines:
            return {}
        
        files = self.guidelines[category]
        total_size = sum(f['size_bytes'] for f in files.values())
        
        return {
            'category': category,
            'file_count': len(files),
            'total_size_mb': total_size / 1024 / 1024,
            'files': list(files.keys())
        }

class VoiceDrivenJTS:
    """Voice-driven interface for JTS guidelines"""
    
    def __init__(self):
        self.decision_engine = JTSDecisionEngine()
        self.conversation_history = []
    
    def process_voice_query(self, query: str) -> Dict:
        """Process voice query and return response"""
        # Add to conversation history
        self.conversation_history.append({
            'type': 'query',
            'content': query,
            'timestamp': None  # Could add actual timestamp
        })
        
        # Extract clinical decision
        decision = self.decision_engine.extract_clinical_decision(query)
        
        # Generate voice response
        voice_response = self.decision_engine.generate_voice_response(decision)
        
        # Add response to history
        self.conversation_history.append({
            'type': 'response',
            'content': voice_response,
            'decision': decision
        })
        
        return {
            'query': query,
            'response': voice_response,
            'decision': decision,
            'confidence': decision['confidence']
        }
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation for clinical documentation"""
        summary_parts = []
        
        for i, entry in enumerate(self.conversation_history):
            if entry['type'] == 'query':
                summary_parts.append(f"Query {i//2 + 1}: {entry['content']}")
            elif entry['type'] == 'response':
                summary_parts.append(f"Response: {entry['content'][:100]}...")
        
        return "\n".join(summary_parts)

def main():
    """Test the JTS decision engine"""
    jts = VoiceDrivenJTS()
    
    # Test queries
    test_queries = [
        "How do I assess airway in trauma?",
        "What's the treatment for hemorrhagic shock?",
        "How to manage spinal cord injury?",
        "What medications for pain management?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = jts.process_voice_query(query)
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']}")

if __name__ == "__main__":
    main() 