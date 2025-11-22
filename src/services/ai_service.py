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

    def analyze_comments(self, comments: List[Dict], filter_params: Optional[Dict] = None) -> Dict:
        """
        Analyze public comments to identify themes, sentiment, and key concerns.

        Args:
            comments: List of comment dictionaries
            filter_params: Optional filters (fmp, position, state, etc.)

        Returns:
            Dict with analysis results including themes, sentiment breakdown, key concerns
        """
        try:
            if not comments:
                return {
                    'success': False,
                    'error': 'No comments provided for analysis'
                }

            if not self.api_key:
                return self._fallback_response('comment analysis', 'Claude API key not configured')

            # Prepare comment data for analysis (limit to prevent token overflow)
            comment_texts = []
            for c in comments[:100]:  # Limit to 100 comments
                comment_entry = {
                    'text': c.get('commentText', c.get('comment_text', ''))[:500],  # Truncate long comments
                    'position': c.get('position', 'Unknown'),
                    'commenterType': c.get('commenterType', c.get('commenter_type', 'Unknown')),
                    'state': c.get('state', ''),
                    'organization': c.get('organization', ''),
                    'fmp': c.get('actionFmp', c.get('action_fmp', ''))
                }
                if comment_entry['text']:  # Only include non-empty comments
                    comment_texts.append(comment_entry)

            if not comment_texts:
                return {
                    'success': False,
                    'error': 'No valid comment text found for analysis'
                }

            # Build analysis prompt
            filter_description = ""
            if filter_params:
                filters = []
                if filter_params.get('fmp'):
                    filters.append(f"FMP: {filter_params['fmp']}")
                if filter_params.get('position'):
                    filters.append(f"Position: {filter_params['position']}")
                if filter_params.get('state'):
                    filters.append(f"State: {filter_params['state']}")
                if filters:
                    filter_description = f"Filtered by: {', '.join(filters)}\n"

            prompt = self._build_comment_analysis_prompt(comment_texts, filter_description, len(comments))

            # Call Claude API with extended token limit for analysis
            response = self._call_claude_api(prompt)

            # Process response
            result = self._process_response(response)
            result['comments_analyzed'] = len(comment_texts)
            result['total_comments'] = len(comments)

            return result

        except Exception as e:
            logger.error(f"Error analyzing comments: {e}")
            return {
                'success': False,
                'error': str(e),
                'answer': 'Unable to analyze comments at this time. Please try again later.'
            }

    def _build_comment_analysis_prompt(self, comments: List[Dict], filter_description: str, total_count: int) -> Dict:
        """Build prompt for comment analysis"""

        system_prompt = """You are an expert analyst for the South Atlantic Fishery Management Council (SAFMC). Your task is to analyze public comments submitted during the FMP amendment process and provide actionable insights.

Analyze the provided comments and generate a structured analysis with:

1. **EXECUTIVE SUMMARY** (2-3 sentences)
   - Overall sentiment and participation level
   - Most significant finding

2. **KEY THEMES** (Top 3-5 themes)
   For each theme:
   - Theme name
   - Frequency (how many comments mention it)
   - Representative quote(s)

3. **SENTIMENT ANALYSIS**
   - Support vs Opposition breakdown
   - Key reasons for each position
   - Notable concerns from neutral commenters

4. **STAKEHOLDER BREAKDOWN**
   - Analysis by commenter type (Commercial, Recreational, For-Hire, NGO, etc.)
   - Geographic patterns if apparent

5. **EMERGING CONCERNS**
   - Issues raised that may need Council attention
   - Unexpected or novel perspectives

6. **RECOMMENDATIONS**
   - Suggested responses or actions
   - Areas needing clarification in amendment language

Be specific and cite actual comment content where helpful. Focus on actionable insights for Council staff and members."""

        comments_json = json.dumps(comments, indent=2)

        user_content = f"""{filter_description}
Total comments in database: {total_count}
Comments included in this analysis: {len(comments)}

COMMENTS DATA:
{comments_json}

Please provide a comprehensive analysis following the structure outlined above. Be specific and reference actual comment content where relevant."""

        return {
            'model': self.model,
            'max_tokens': 2000,  # Extended for detailed analysis
            'temperature': 0,
            'messages': [
                {
                    'role': 'user',
                    'content': f"{system_prompt}\n\n{user_content}"
                }
            ]
        }

    def summarize_comment_group(self, comments: List[Dict], group_by: str = 'fmp') -> Dict:
        """
        Generate summaries for groups of comments (by FMP, position, state, etc.)

        Args:
            comments: List of comment dictionaries
            group_by: Field to group by ('fmp', 'position', 'state', 'commenterType')

        Returns:
            Dict with summaries for each group
        """
        try:
            if not comments:
                return {'success': False, 'error': 'No comments provided'}

            if not self.api_key:
                return self._fallback_response('comment summary', 'Claude API key not configured')

            # Group comments
            groups = {}
            for c in comments:
                key_map = {
                    'fmp': c.get('actionFmp', c.get('action_fmp', 'Unspecified')),
                    'position': c.get('position', 'Unknown'),
                    'state': c.get('state', 'Unknown'),
                    'commenterType': c.get('commenterType', c.get('commenter_type', 'Unknown'))
                }
                key = key_map.get(group_by, 'Unknown') or 'Unknown'
                if key not in groups:
                    groups[key] = []
                groups[key].append(c)

            # Generate summary for each group
            summaries = {}
            for group_name, group_comments in groups.items():
                if len(group_comments) < 2:
                    summaries[group_name] = {
                        'count': len(group_comments),
                        'summary': f"Only {len(group_comments)} comment(s) in this group."
                    }
                    continue

                # Quick summary for each group
                sample_texts = [
                    c.get('commentText', c.get('comment_text', ''))[:200]
                    for c in group_comments[:20]
                ]

                prompt = {
                    'model': self.model,
                    'max_tokens': 500,
                    'temperature': 0,
                    'messages': [{
                        'role': 'user',
                        'content': f"""Summarize these {len(group_comments)} public comments about "{group_name}" in 2-3 sentences. Focus on the main concerns and positions expressed.

Sample comments:
{json.dumps(sample_texts, indent=2)}

Provide a concise summary:"""
                    }]
                }

                try:
                    response = self._call_claude_api(prompt)
                    result = self._process_response(response)
                    summaries[group_name] = {
                        'count': len(group_comments),
                        'summary': result.get('answer', 'Unable to generate summary')
                    }
                except Exception as e:
                    summaries[group_name] = {
                        'count': len(group_comments),
                        'summary': f"Error generating summary: {str(e)}"
                    }

            return {
                'success': True,
                'group_by': group_by,
                'summaries': summaries,
                'total_comments': len(comments),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error summarizing comment groups: {e}")
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
