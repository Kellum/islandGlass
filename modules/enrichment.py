"""
Enrichment module for contractor website analysis using Claude API
"""
import os
import json
import re
import time
import aiohttp
import asyncio
from typing import Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from modules.database import Database

# Load environment variables
load_dotenv()


class ContractorEnrichment:
    """Handle contractor enrichment using website analysis and Claude API"""

    def __init__(self, db: Optional[Database] = None):
        """Initialize enrichment with Claude API client

        Args:
            db: Optional Database instance (useful for authenticated access).
                If not provided, creates new instance with service role key for RLS bypass.
        """
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in environment variables")

        self.client = Anthropic(api_key=self.api_key)

        # Use provided database or create new instance with service role key
        if db:
            self.db = db
        else:
            # Use service role key to bypass RLS when no authenticated DB provided
            from supabase import create_client
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if url and service_key:
                # Create a special DB instance with service role
                self.db = Database()
                self.db.client = create_client(url, service_key)
            else:
                self.db = Database()

        # Claude API settings
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 2000

    async def fetch_website_content(self, url: str) -> Optional[str]:
        """
        Fetch website content using aiohttp
        Returns cleaned text content or None if failed
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Basic HTML cleaning - remove scripts, styles, tags
                        cleaned = self._clean_html(html)
                        # Truncate to reasonable size (avoid huge API calls)
                        return cleaned[:15000]  # ~4000 tokens
                    else:
                        print(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
        except asyncio.TimeoutError:
            print(f"Timeout fetching {url}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def _clean_html(self, html: str) -> str:
        """
        Basic HTML cleaning to extract text content
        """
        # Remove script and style tags with their content
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        html = re.sub(r'<[^>]+>', ' ', html)

        # Clean up whitespace
        html = re.sub(r'\s+', ' ', html)
        html = html.strip()

        return html

    def analyze_with_claude(self, website_content: str, company_name: str, city: str, contractor_id: int = None) -> Optional[Dict]:
        """
        Analyze website content using Claude API
        Returns enrichment data in structured format
        """
        prompt = f"""Analyze this contractor's website and determine if they are a good fit for glazing services (frameless showers, cabinet glass, tabletops, protective glass tops, glass railings, storefront systems, window/IGU replacement).

Website content:
{website_content}

Extract the following in JSON format:
{{
  "contact_email": "primary email or null",
  "contact_person": "owner/manager name or null",
  "specializations": ["specific services like bathroom remodeling, custom homes, commercial buildouts, etc"],
  "company_type": "residential|commercial|both",
  "glazing_relevant_services": ["which of their services need our glazing products"],
  "glazing_opportunity_types": ["which glazing services they likely need: frameless_showers|cabinet_glass|tabletops|protective_tops|glass_railings|storefront|window_replacement"],
  "company_age": "years in business or null",
  "team_size_indicator": "small|medium|large or null",
  "project_examples": ["any bathroom/kitchen/commercial projects mentioned"],
  "uses_subcontractors": "likely|unlikely|unknown",
  "glazing_opportunity_score": 1-10 based on how much they need our services,
  "disqualify_reason": "if score <5, explain why they don't need glazing services, else null",
  "profile_notes": "2-3 sentence summary of their business and glazing fit",
  "outreach_angle": "best hook mentioning their specific projects that need our glazing"
}}

Scoring guide:
- 9-10: Does bathroom remodels, custom showers, or commercial storefront
- 7-8: Does kitchen remodels (cabinet glass), custom homes (multiple glass needs), or office buildouts
- 5-6: Does decks/pools (glass railings) or custom furniture (tabletops)
- 1-4: Roofing, HVAC, landscaping, foundation, electrical - does NOT need glazing

Be conservative with scoring - better to underscore than overscore.

Return ONLY the JSON object, no additional text."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track API usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Calculate cost (Claude Sonnet 4 pricing)
            # Input: $3 per million tokens, Output: $15 per million tokens
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost

            # Log usage to database
            self.db.log_api_usage(
                action_type="enrichment",
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=total_cost,
                contractor_id=contractor_id,
                success=True
            )

            print(f"API Usage - Enrichment: {input_tokens + output_tokens} tokens (${total_cost:.4f})")

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Try to parse JSON
            # Sometimes Claude adds markdown code blocks, so clean those
            if response_text.startswith('```'):
                response_text = re.sub(r'^```json?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            enrichment_data = json.loads(response_text)

            # Validate required fields
            if not isinstance(enrichment_data.get('glazing_opportunity_score'), int):
                print(f"Invalid score in response for {company_name}")
                return None

            return enrichment_data

        except json.JSONDecodeError as e:
            print(f"Failed to parse Claude response for {company_name}: {e}")
            print(f"Response was: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"Error calling Claude API for {company_name}: {e}")
            return None

    async def enrich_contractor(self, contractor_id: int) -> Dict:
        """
        Enrich a single contractor with website analysis
        Returns status dict with success/failure and enrichment data
        """
        result = {
            "success": False,
            "contractor_id": contractor_id,
            "message": "",
            "enrichment_data": None
        }

        # Get contractor from database
        contractor = self.db.get_contractor_by_id(contractor_id)
        if not contractor:
            result["message"] = "Contractor not found"
            return result

        company_name = contractor.get("company_name", "Unknown")
        website = contractor.get("website")
        city = contractor.get("city", "Jacksonville")

        # Check if website exists
        if not website:
            result["message"] = "No website available for enrichment"
            # Update enrichment status to failed
            self.db.update_contractor(contractor_id, {
                "enrichment_status": "failed",
                "disqualify_reason": "No website available"
            })
            return result

        print(f"Enriching {company_name}...")

        # Fetch website content
        website_content = await self.fetch_website_content(website)
        if not website_content:
            result["message"] = "Failed to fetch website content"
            self.db.update_contractor(contractor_id, {
                "enrichment_status": "failed"
            })
            return result

        print(f"Fetched {len(website_content)} chars from {website}")

        # Analyze with Claude
        enrichment_data = self.analyze_with_claude(website_content, company_name, city, contractor_id)
        if not enrichment_data:
            result["message"] = "Failed to analyze website with Claude"
            self.db.update_contractor(contractor_id, {
                "enrichment_status": "failed"
            })
            return result

        # Extract score
        score = enrichment_data.get("glazing_opportunity_score", 0)

        # Only save contractors with score >= 5
        if score < 5:
            result["message"] = f"Score {score} below threshold (5). Not saving."
            result["enrichment_data"] = enrichment_data
            # Mark as failed with disqualify reason
            self.db.update_contractor(contractor_id, {
                "enrichment_status": "failed",
                "disqualify_reason": enrichment_data.get("disqualify_reason", "Score below threshold")
            })
            return result

        # Prepare update data
        update_data = {
            "email": enrichment_data.get("contact_email") or contractor.get("email"),
            "contact_person": enrichment_data.get("contact_person") or contractor.get("contact_person"),
            "specializations": ",".join(enrichment_data.get("specializations", [])),
            "company_type": enrichment_data.get("company_type") or contractor.get("company_type"),
            "glazing_opportunity_types": ",".join(enrichment_data.get("glazing_opportunity_types", [])),
            "uses_subcontractors": enrichment_data.get("uses_subcontractors", "unknown"),
            "lead_score": score,
            "profile_notes": enrichment_data.get("profile_notes", ""),
            "outreach_angle": enrichment_data.get("outreach_angle", ""),
            "enrichment_status": "completed"
        }

        # Update contractor in database
        success = self.db.update_contractor(contractor_id, update_data)

        if success:
            result["success"] = True
            result["message"] = f"Successfully enriched {company_name} (Score: {score})"
            result["enrichment_data"] = enrichment_data
            print(f"✓ Enriched {company_name}: Score {score}/10")
        else:
            result["message"] = "Failed to update database"

        # Rate limiting - be respectful to Claude API
        await asyncio.sleep(1)

        return result

    async def enrich_multiple_contractors(self, contractor_ids: list) -> list:
        """
        Enrich multiple contractors sequentially
        Returns list of result dicts
        """
        results = []

        for contractor_id in contractor_ids:
            result = await self.enrich_contractor(contractor_id)
            results.append(result)

            # Progress indicator
            print(f"Progress: {len(results)}/{len(contractor_ids)}")

        return results

    def get_pending_enrichments(self, limit: int = 50) -> list:
        """
        Get contractors that need enrichment
        Returns list of contractor dicts with enrichment_status='pending'
        """
        try:
            contractors = self.db.client.table("contractors") \
                .select("*") \
                .eq("enrichment_status", "pending") \
                .not_.is_("website", "null") \
                .limit(limit) \
                .execute()

            return contractors.data if contractors.data else []
        except Exception as e:
            print(f"Error fetching pending enrichments: {e}")
            return []


# Helper function for easy async usage
def run_enrichment(contractor_id: int) -> Dict:
    """
    Synchronous wrapper for enriching a single contractor
    """
    enricher = ContractorEnrichment()
    result = asyncio.run(enricher.enrich_contractor(contractor_id))
    return result


def run_batch_enrichment(contractor_ids: list) -> list:
    """
    Synchronous wrapper for enriching multiple contractors
    """
    enricher = ContractorEnrichment()
    results = asyncio.run(enricher.enrich_multiple_contractors(contractor_ids))
    return results
