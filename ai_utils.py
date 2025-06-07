# -*- coding: utf-8 -*-
"""
AI Utilities for PRISMA 2020 Tool
Handles AI-powered text improvement using Groq API
"""

import os
from typing import Optional, Dict, Any
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    print("Warning: groq library not available. AI features disabled. Install with: pip install groq")
    GROQ_AVAILABLE = False

class AIUtils:
    """
    AI-powered text improvement utilities using Groq API
    Provides academic writing enhancement for systematic reviews
    """
    
    def __init__(self):
        """Initialize AI utilities with Groq client"""
        self.client = None
        self.available_models = [
            "llama3-8b-8192",
            "llama3-70b-8192", 
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        self.default_model = "llama3-70b-8192"
        self.last_api_key = None
        
        if GROQ_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client with API key"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                print("Warning: GROQ_API_KEY not found in environment variables")
                self.client = None
                return
                
            # Only reinitialize if API key changed
            if self.last_api_key != api_key:
                self.client = Groq(api_key=api_key)
                self.last_api_key = api_key
                print("Groq AI client initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.client = None
    
    def update_api_key(self, api_key: str):
        """Update API key and reinitialize client"""
        if api_key and api_key.strip():
            os.environ['GROQ_API_KEY'] = api_key.strip()
        else:
            # Clear the environment variable if key is empty
            os.environ.pop('GROQ_API_KEY', None)
        
        if GROQ_AVAILABLE:
            self._initialize_client()
    
    def is_available(self) -> bool:
        """Check if AI functionality is available"""
        return GROQ_AVAILABLE and self.client is not None
    
    def validate_api_connection(self) -> Dict[str, Any]:
        """
        Validate API connection and return status
        
        Returns:
            Dictionary with connection status and details
        """
        result = {
            "available": False,
            "library_installed": GROQ_AVAILABLE,
            "api_key_present": bool(os.getenv('GROQ_API_KEY')),
            "client_initialized": self.client is not None,
            "error": None
        }
        
        if not GROQ_AVAILABLE:
            result["error"] = "Groq library not installed"
            return result
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            result["error"] = "API key not provided"
            return result
        
        try:
            # Try to initialize client if not already done
            if not self.client:
                self._initialize_client()
            
            if self.client:
                # Test the connection with a simple request
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {
                            "role": "user",
                            "content": "Hello"
                        }
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                
                if response and response.choices:
                    result["available"] = True
                    result["model"] = self.default_model
                else:
                    result["error"] = "Invalid API response"
                    
        except Exception as e:
            result["error"] = str(e)
            self.client = None
        
        return result
    
    def improve_text(self, text: str, context: str = "", model: str = None) -> Optional[str]:
        """
        Improve text using AI for academic writing
        
        Args:
            text: Text to improve
            context: Context information (e.g., section name)  
            model: Specific model to use (optional)
            
        Returns:
            Improved text or None if failed
        """
        if not self.is_available():
            print("AI functionality not available")
            return None
            
        if not text.strip():
            print("Empty text provided")
            return None
            
        try:
            # Select model
            selected_model = model if model in self.available_models else self.default_model
            
            # Construct prompt
            prompt = self._create_improvement_prompt(text, context)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2048,
                top_p=0.9
            )
            
            improved_text = response.choices[0].message.content.strip()
            
            # Clean the response to remove any explanations or formatting
            improved_text = self._clean_ai_response(improved_text, text)
            
            # Basic validation
            if len(improved_text) < len(text) * 0.3:
                print("Warning: Improved text seems too short, using original")
                return text
                
            print("Text improvement completed successfully")
            return improved_text
            
        except Exception as e:
            print(f"Error improving text with AI: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI text improvement"""
        return """You are an expert academic writing assistant specializing in systematic reviews and meta-analyses. Your task is to improve scientific text according to the following criteria:

1. **Academic Style**: Use formal, precise academic language appropriate for peer-reviewed publications
2. **Clarity**: Ensure the text is clear, concise, and well-structured
3. **Scientific Rigor**: Maintain scientific accuracy and appropriate terminology
4. **Flow**: Improve logical flow and coherence between ideas
5. **PRISMA 2020 Compliance**: Ensure adherence to PRISMA 2020 guidelines when applicable
6. **Redundancy**: Remove unnecessary repetition while preserving important information
7. **Grammar**: Correct any grammatical errors and improve sentence structure

Important guidelines:
- Preserve all factual information and data
- Maintain the original meaning and intent
- Use active voice where appropriate
- Ensure proper scientific terminology
- Keep the same general length unless significant improvement requires changes
- Focus on systematic review and meta-analysis conventions"""

    def _create_improvement_prompt(self, text: str, context: str) -> str:
        """
        Create specific prompt for text improvement
        
        Args:
            text: Text to improve
            context: Context information
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Improve the following text from a systematic review. This text is part of the "{context}" section.

Requirements:
- Enhance academic writing quality while preserving all factual content
- Improve clarity, flow, and scientific rigor
- Ensure compliance with systematic review writing standards
- Remove redundancy and improve sentence structure
- Maintain appropriate academic tone throughout
- CRITICAL: Preserve ALL citations in the format [1], [2], [1,2], etc. exactly as they appear

IMPORTANT: Return ONLY the improved text. Do not include explanations, comments, or descriptions of changes made. Keep all citations [1], [2], etc. in their exact positions or move them appropriately within sentences.

Original text:
{text}

Improved text:"""

        return prompt
    
    def _clean_ai_response(self, response_text: str, original_text: str) -> str:
        """
        Clean AI response to extract only the improved text while preserving citations
        
        Args:
            response_text: Raw response from AI
            original_text: Original text for fallback
            
        Returns:
            Cleaned improved text with preserved citations
        """
        import re
        
        # Extract citations from original text
        original_citations = re.findall(r'\[\d+(?:,\d+)*\]', original_text)
        
        # Remove common explanation patterns
        response_text = response_text.strip()
        
        # Remove lines that start with explanation markers
        lines = response_text.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            r'^(I made|I changed|Here|The following|Changes made|Improvements|Note:|Notes:|Explanation:)',
            r'^(Here\'s|Here is|This|These)',
            r'^\*',  # Bullet points
            r'^-',   # Dash points
            r'^•',   # Bullet points
            r'^\d+\.',  # Numbered lists
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that match explanation patterns
            skip_line = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    skip_line = True
                    break
            
            if not skip_line:
                cleaned_lines.append(line)
        
        # If we have cleaned lines, join them
        if cleaned_lines:
            cleaned_text = '\n'.join(cleaned_lines).strip()
            
            # Check if citations are preserved
            improved_citations = re.findall(r'\[\d+(?:,\d+)*\]', cleaned_text)
            
            # If citations are missing, try to restore them intelligently
            if original_citations and len(improved_citations) < len(original_citations):
                # Simple restoration: add missing citations at the end of sentences
                missing_citations = [cite for cite in original_citations if cite not in improved_citations]
                if missing_citations:
                    cleaned_text += " " + " ".join(missing_citations)
            
            # If the cleaned text is significantly shorter than original, it might be over-cleaned
            if len(cleaned_text) > 10:  # Minimum reasonable length
                return cleaned_text
        
        # Fallback: try to extract text after common prompts
        fallback_patterns = [
            r'Improved text:\s*(.*)',
            r'Here is the improved .*?:\s*(.*)',
            r'Corrected .*?:\s*(.*)',
            r'Enhanced .*?:\s*(.*)'
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) > 10:
                    return extracted
        
        # Final fallback: return the first substantial paragraph
        paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
        for paragraph in paragraphs:
            if len(paragraph) > 20 and not any(re.match(pattern, paragraph, re.IGNORECASE) for pattern in skip_patterns):
                return paragraph
        
        # If all else fails, return original
        return original_text
    
    def suggest_content(self, section_name: str, topic: str = "") -> Optional[str]:
        """
        Suggest content for a specific PRISMA section
        
        Args:
            section_name: Name of the PRISMA section
            topic: Research topic/subject (optional)
            
        Returns:
            Suggested content or None if failed
        """
        if not self.is_available():
            print("AI functionality not available")
            return None
            
        try:
            prompt = self._create_suggestion_prompt(section_name, topic)
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=1024,
                top_p=0.9
            )
            
            suggestion = response.choices[0].message.content.strip()
            print(f"Content suggestion generated for {section_name}")
            return suggestion
            
        except Exception as e:
            print(f"Error generating content suggestion: {e}")
            return None
    
    def _create_suggestion_prompt(self, section_name: str, topic: str) -> str:
        """Create prompt for content suggestions"""
        topic_info = f" The research topic is: {topic}." if topic else ""
        
        return f"""Please provide guidance and suggestions for writing the "{section_name}" section of a systematic review following PRISMA 2020 guidelines.{topic_info}

Include:
1. Key elements that should be covered
2. Recommended structure and organization
3. Specific phrases or terminology commonly used
4. Important considerations for this section
5. A brief example or template if helpful

Focus on practical, actionable advice that helps researchers write high-quality systematic reviews."""

    def check_completeness(self, sections_content: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze completeness of systematic review sections
        
        Args:
            sections_content: Dictionary of section names and content
            
        Returns:
            Analysis results
        """
        if not self.is_available():
            return {"error": "AI functionality not available"}
            
        try:
            # Basic analysis without AI call for now
            analysis = {
                "completion_rate": 0,
                "completed_sections": [],
                "empty_sections": [],
                "recommendations": []
            }
            
            completed = 0
            for section, content in sections_content.items():
                if content.strip():
                    completed += 1
                    analysis["completed_sections"].append(section)
                else:
                    analysis["empty_sections"].append(section)
            
            analysis["completion_rate"] = completed / len(sections_content) if sections_content else 0
            
            # Generate recommendations
            if analysis["empty_sections"]:
                analysis["recommendations"].append(
                    f"Complete the following sections: {', '.join(analysis['empty_sections'])}"
                )
            
            if analysis["completion_rate"] < 0.5:
                analysis["recommendations"].append(
                    "Consider focusing on core sections first: Introduction, Methods, Results, Discussion"
                )
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing completeness: {e}")
            return {"error": str(e)}
    
    def get_writing_tips(self, section_name: str) -> Dict[str, Any]:
        """
        Get writing tips for a specific section
        
        Args:
            section_name: Name of the section
            
        Returns:
            Dictionary with writing tips and guidelines
        """
        # Static tips database - could be enhanced with AI
        tips_database = {
            "Título": {
                "key_points": [
                    "Clearly identify the document as a systematic review",
                    "Include 'systematic review' or 'meta-analysis' in the title",
                    "Be specific about the population and intervention studied"
                ],
                "examples": [
                    "Effects of exercise interventions on depression: a systematic review and meta-analysis",
                    "Systematic review of mobile health interventions for diabetes management"
                ]
            },
            "Resumo": {
                "key_points": [
                    "Follow structured abstract format",
                    "Include all key elements: background, objectives, data sources, study selection, data extraction, data synthesis, results, limitations, conclusions",
                    "Stay within word limits (usually 250-300 words)"
                ],
                "structure": [
                    "Background and Objectives",
                    "Data Sources and Study Selection", 
                    "Data Extraction and Synthesis",
                    "Results",
                    "Limitations and Conclusions"
                ]
            },
            "Métodos - Estratégia de Busca": {
                "key_points": [
                    "Present complete search strategy for at least one database",
                    "Include all search terms, Boolean operators, and limits",
                    "Ensure reproducibility",
                    "Report search dates"
                ],
                "elements": [
                    "Search terms and synonyms",
                    "Boolean operators (AND, OR, NOT)",
                    "Field tags (title, abstract, MeSH terms)",
                    "Limits (date, language, study type)"
                ]
            }
        }
        
        return tips_database.get(section_name, {
            "key_points": ["Follow PRISMA 2020 guidelines for this section"],
            "note": "Specific tips not available for this section"
        })
