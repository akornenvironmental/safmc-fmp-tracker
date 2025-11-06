"""
AI Query Service for SAFMC FMP Tracker
Integrates with Claude API for intelligent document analysis and queries
"""

import os
import logging
from typing import Dict, List, Optional
import json
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered queries and analysis using Claude API"""

    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.api_url = 'https://api.anthropic.com/v1/messages'
        self.model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        self.max_tokens = 1000

    def query(self, question: str, context: Optional[Dict] = None) -> Dict:
        """
        Query the AI system with an FMP-related question

        Args:
            question: User's question
            context: Additional context data

        Returns:
            Dict with success status and AI response
        """
        try:
            if not self.api_key:
                return self._fallback_response(question, 'Claude API key not configured')

            # Build context
            query_context = self._build_context(question, context or {})

            # Build prompt
            prompt = self._build_prompt(question, query_context)

            # Call Claude API
            response = self._call_claude_api(prompt)

            # Process response
            result = self._process_response(response)

            # Log query
            self._log_query(question, result['success'])

            return result

        except Exception as e:
            logger.error(f"Error in AI query: {e}")
            return {
                'success': False,
                'error': str(e),
                'answer': self._generate_fallback(question)
            }

    def analyze_patterns(self, actions: List[Dict]) -> Dict:
        """Analyze FMP development patterns"""
        try:
            question = (
                "Analyze the current FMP development patterns and identify any bottlenecks "
                "or trends in the SAFMC process. Provide insights on timeline efficiency "
                "and recommendations for improvement."
            )

            context = {
                'analysis_type': 'pattern_analysis',
                'actions': actions[:20],  # Limit to avoid token overflow
                'total_actions': len(actions)
            }

            return self.query(question, context)

        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {'success': False, 'error': str(e)}

    def generate_status_report(self, actions: List[Dict], meetings: List[Dict]) -> Dict:
        """Generate comprehensive status report"""
        try:
            question = (
                "Generate a comprehensive status report of all current SAFMC FMP development "
                "activities, highlighting key actions in each phase and any urgent items "
                "requiring attention."
            )

            context = {
                'report_type': 'status_summary',
                'actions': actions[:15],
                'meetings': meetings[:10]
            }

            return self.query(question, context)

        except Exception as e:
            logger.error(f"Error generating status report: {e}")
            return {'success': False, 'error': str(e)}

    def search_content(self, search_terms: str, actions: List[Dict]) -> Dict:
        """Search for specific information across FMP documents"""
        try:
            question = (
                f"Search for information about: {search_terms}. "
                "Provide relevant details from SAFMC FMP documents and current actions."
            )

            # Filter relevant actions
            relevant_actions = [
                a for a in actions
                if search_terms.lower() in str(a).lower()
            ][:10]

            context = {
                'search_terms': search_terms,
                'search_type': 'content_search',
                'relevant_actions': relevant_actions
            }

            return self.query(question, context)

        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return {'success': False, 'error': str(e)}

    def _build_context(self, question: str, additional_context: Dict) -> Dict:
        """Build context data for AI query"""
        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'safmc_info': self._get_safmc_knowledge_base(),
            **additional_context
        }

        return context

    def _build_prompt(self, question: str, context: Dict) -> Dict:
        """Build Claude API prompt"""
        system_prompt = """You are an expert assistant for the South Atlantic Fishery Management Council (SAFMC) FMP Development Tracker. You help users understand fishery management processes, track amendment progress, and analyze FMP development data.

SAFMC manages federal fisheries from North Carolina to Florida through eight fishery management plans. The FMP development process typically involves: Scoping → Development → Review → Final Action → Submitted to NOAA.

Your responses should be:
- Accurate and based ONLY on the provided data - do not make assumptions or extrapolate
- Clear and accessible to both fishery professionals and the public
- Focused on SAFMC-specific processes and information
- Helpful for tracking FMP development progress
- If you don't have specific information, clearly state that rather than guessing

IMPORTANT: Minimize hallucinations and over-interpretations. Stick strictly to the data provided. If uncertain, say so explicitly.

Current SAFMC Context:
{safmc_info}

Additional Context:
{context}""".format(
            safmc_info=json.dumps(context.get('safmc_info', {}), indent=2),
            context=json.dumps({k: v for k, v in context.items() if k != 'safmc_info'}, indent=2)
        )

        return {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': 0,  # Set to 0 to minimize hallucinations
            'messages': [
                {
                    'role': 'user',
                    'content': f"{system_prompt}\n\nUser Question: {question}\n\nPlease provide a comprehensive, helpful response based ONLY on the SAFMC data and context provided above. If the data doesn't contain the answer, clearly state that."
                }
            ]
        }

    def _call_claude_api(self, prompt: Dict) -> Dict:
        """Call Claude API"""
        if not self.api_key:
            raise ValueError('Claude API key not configured')

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=prompt,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")

        return response.json()

    def _process_response(self, response: Dict) -> Dict:
        """Process Claude API response"""
        if response.get('content') and len(response['content']) > 0:
            return {
                'success': True,
                'answer': response['content'][0]['text'],
                'usage': response.get('usage', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            raise ValueError('Invalid response format from Claude API')

    def _get_safmc_knowledge_base(self) -> Dict:
        """Get SAFMC knowledge base information"""
        return {
            'organization': 'South Atlantic Fishery Management Council',
            'jurisdiction': 'North Carolina to Florida (federal waters)',
            'managed_fisheries': [
                'Snapper Grouper',
                'Coastal Migratory Pelagics (Mackerel & Cobia)',
                'Dolphin Wahoo',
                'Coral and Live Bottom Habitat',
                'Golden Crab',
                'Shrimp',
                'Spiny Lobster',
                'Sargassum'
            ],
            'process_stages': [
                'Scoping - Initial public input and alternative development',
                'Development - Document preparation and analysis',
                'Review - Public hearings and comment periods',
                'Final Action - Council final approval',
                'Submitted - Sent to NOAA Fisheries for rulemaking'
            ],
            'typical_timeline': '24-36 months from initiation to implementation',
            'key_legislation': [
                'Magnuson-Stevens Fishery Conservation and Management Act',
                'National Environmental Policy Act (NEPA)',
                'Regulatory Flexibility Act'
            ]
        }

    def _generate_fallback(self, question: str) -> str:
        """Generate fallback response when AI fails"""
        fallbacks = {
            'status': 'I can provide status information about current FMP actions. Please try refreshing the data or contact SAFMC staff directly.',
            'timeline': 'FMP development typically takes 24-36 months from initiation through NOAA approval. Specific timelines vary by complexity.',
            'process': 'The SAFMC FMP process includes: Scoping → Development → Public Review → Final Action → NOAA Rulemaking.',
            'documents': 'Documents are available on the SAFMC website at safmc.net. Each amendment has its own dedicated page with relevant materials.'
        }

        question_lower = question.lower()

        for key, response in fallbacks.items():
            if key in question_lower:
                return response

        return 'I apologize, but I cannot process your question at this time. Please visit safmc.net for the most current information or contact SAFMC staff directly.'

    def _fallback_response(self, question: str, reason: str) -> Dict:
        """Return fallback response"""
        return {
            'success': False,
            'error': reason,
            'answer': self._generate_fallback(question),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _log_query(self, question: str, success: bool, error: str = ''):
        """Log AI query for monitoring"""
        # In a real implementation, this would log to database
        logger.info(f"AI Query - Success: {success}, Question: {question[:100]}")
        if error:
            logger.error(f"AI Query Error: {error}")
