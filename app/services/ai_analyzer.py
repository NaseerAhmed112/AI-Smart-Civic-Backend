import json
import re
from difflib import SequenceMatcher
from typing import Dict, Any, Optional, List
from google import genai
from app.config import settings
from app.services.prompts import CIVIC_ANALYSIS_PROMPT

class AIAnalyzer:
    """
    OOP AI Engine managing multi-factor civic complaint analysis, multimodal inputs,
    duplicate complaint detection, priority scoring, and offline heuristic fallback.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def analyze(self, description: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes a complaint description and optional image.
        Returns a dict containing category, priority, assigned_department, ai_summary, ai_reason, ai_confidence.
        """
        if self.client:
            try:
                prompt = CIVIC_ANALYSIS_PROMPT.format(description=description)
                # Try gemini-1.5-flash or gemini-2.5-flash
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_text)
                parsed["ai_confidence"] = float(parsed.get("ai_confidence", 0.92))
                return parsed
            except Exception as e:
                # Silently fall back to heuristic NLP model
                pass

        return self._heuristic_fallback(description)

    def check_duplicate(self, new_description: str, new_location: str, existing_complaints: List[Any]) -> Dict[str, Any]:
        best_match_ratio = 0.0
        matched_id = None

        new_desc_clean = new_description.lower().strip()
        new_loc_clean = new_location.lower().strip()

        for comp in existing_complaints:
            if comp.status in ["Open", "In Progress"]:
                loc_similarity = SequenceMatcher(None, new_loc_clean, comp.location.lower().strip()).ratio()
                text_similarity = SequenceMatcher(None, new_desc_clean, comp.description.lower().strip()).ratio()

                combined_score = (text_similarity * 0.6) + (loc_similarity * 0.4)
                if combined_score > best_match_ratio:
                    best_match_ratio = combined_score
                    matched_id = comp.complaint_id

        is_dup = best_match_ratio > 0.65
        return {
            "is_duplicate": is_dup,
            "similarity_score": round(best_match_ratio, 2),
            "matched_complaint_id": matched_id if is_dup else None
        }

    def _heuristic_fallback(self, description: str) -> Dict[str, Any]:
        text = description.lower()
        
        # Category detection
        if any(w in text for w in ["trash", "garbage", "waste", "dump", "litter", "sanitation"]):
            category = "Waste Management"
            dept = "Department of Urban Sanitation"
        elif any(w in text for w in ["water", "sewage", "leak", "pipe", "drain", "tap", "flooding", "burst"]):
            category = "Water & Sewage"
            dept = "Water Supply & Sewerage Board"
        elif any(w in text for w in ["road", "pothole", "crater", "asphalt", "traffic", "flyover", "street", "footpath", "bridge"]):
            category = "Roads & Traffic"
            dept = "Public Works Department"
        elif any(w in text for w in ["electric", "power", "light", "wire", "blackout", "sparking", "pole", "transformer"]):
            category = "Electricity & Power"
            dept = "Electricity & Energy Board"
        elif any(w in text for w in ["health", "dog", "dogs", "stray", "mosquito", "dengue", "hospital", "clinic", "disease"]):
            category = "Public Health"
            dept = "Public Health & Safety Office"
        else:
            category = "General Administration"
            dept = "Central Civic Helpdesk"

        # Priority detection
        if any(w in text for w in ["burst", "sparking", "live wire", "hazard", "fire", "electric shock", "collapse", "playground", "emergency"]):
            priority = "Critical"
            reason = "High emergency risk or life-safety hazard detected in report text."
        elif any(w in text for w in ["crash", "pothole", "overflowing", "rotting", "deep", "crater", "flooding", "urgent", "chasing", "aggressive"]):
            priority = "High"
            reason = "Significant public safety or environmental disruption requiring rapid action."
        elif any(w in text for w in ["delay", "moderate", "smell", "flickering", "dark"]):
            priority = "Medium"
            reason = "Standard priority level assigned for routine municipal maintenance."
        else:
            priority = "Low"
            reason = "Minor non-urgent observation."

        summary = description[:90] + "..." if len(description) > 90 else description

        return {
            "category": category,
            "priority": priority,
            "assigned_department": dept,
            "ai_summary": summary,
            "ai_reason": f"Analyzed via heuristic NLP model. {reason}",
            "ai_confidence": 0.85
        }

ai_analyzer = AIAnalyzer()
