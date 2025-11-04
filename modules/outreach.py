"""
Outreach module for generating personalized emails and call scripts using Claude API
"""
import os
import json
import re
from typing import Dict, Optional, List
from anthropic import Anthropic
from dotenv import load_dotenv
from modules.database import Database

# Load environment variables
load_dotenv()


class OutreachGenerator:
    """Generate personalized outreach materials using Claude API"""

    def __init__(self, db: Optional[Database] = None):
        """Initialize outreach generator with Claude API client

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
        self.max_tokens = 1500  # Enough for emails and scripts

    def generate_email_templates(self, contractor: Dict, contractor_id: int = None, num_emails: int = 3) -> Optional[Dict]:
        """
        Generate personalized email templates for a contractor
        Args:
            contractor: Dict with contractor data
            contractor_id: ID of the contractor (optional)
            num_emails: Number of email templates to generate (1-3, default 3)
        Returns dict with email_1, email_2, email_3 (each with subject and body)
        """
        num_emails = max(1, min(3, num_emails))  # Clamp between 1 and 3

        company_name = contractor.get('company_name', 'the contractor')
        specializations = contractor.get('specializations', 'general contracting')
        glazing_opportunities = contractor.get('glazing_opportunity_types', 'glazing services')
        company_type = contractor.get('company_type', 'contractor')
        city = contractor.get('city', 'Jacksonville')
        outreach_angle = contractor.get('outreach_angle', 'your projects')

        prompt = f"""Generate {num_emails} professional email template{'s' if num_emails > 1 else ''} for cold outreach from a glazing company to this contractor:

Contractor profile:
- Company: {company_name}
- Specialization: {specializations}
- Glazing opportunity: {glazing_opportunities}
- Type: {company_type}
- Location: {city}, Florida

Our glazing services:
- Frameless shower enclosures & glass shower doors
- Custom cabinet glass (kitchen & bathroom)
- Glass tabletops & protective glass countertops
- Glass railings (deck, stair, pool)
- Commercial storefront systems & entrances
- Window replacement & IGU (insulated glass unit) replacement

Best outreach angle for this contractor:
{outreach_angle}

Requirements:
- Subject line + body for each email
- Reference their specific work that needs our glazing (e.g., "noticed you do bathroom remodels - we supply frameless showers")
- Mention Florida/Northeast Florida location relevance
- Professional but conversational tone (not salesy)
- Include [EDIT: project name] style placeholders where personalization needed
- Keep body under 120 words
- Include clear call-to-action (schedule call, get quote, etc.)
{f'- Vary the approach across {num_emails} emails (different hooks/angles)' if num_emails > 1 else ''}

Return as JSON:
{{
  {', '.join([f'"email_{i}": {{"subject": "...", "body": "..."}}'for i in range(1, num_emails + 1)])}
}}

Return ONLY the JSON object, no additional text."""

        try:
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
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost

            # Log usage to database
            self.db.log_api_usage(
                action_type="email_generation",
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=total_cost,
                contractor_id=contractor_id,
                success=True
            )

            print(f"API Usage - Email Gen: {input_tokens + output_tokens} tokens (${total_cost:.4f})")

            response_text = response.content[0].text.strip()

            # Clean markdown code blocks if present
            if response_text.startswith('```'):
                response_text = re.sub(r'^```json?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            emails = json.loads(response_text)
            return emails

        except json.JSONDecodeError as e:
            print(f"Failed to parse email templates: {e}")
            print(f"Response: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"Error generating email templates: {e}")
            return None

    def generate_call_scripts(self, contractor: Dict, contractor_id: int = None, num_scripts: int = 2) -> Optional[Dict]:
        """
        Generate personalized call scripts for a contractor
        Args:
            contractor: Dict with contractor data
            contractor_id: ID of the contractor (optional)
            num_scripts: Number of call scripts to generate (1-2, default 2)
        Returns dict with script_1 and script_2
        """
        num_scripts = max(1, min(2, num_scripts))  # Clamp between 1 and 2

        company_name = contractor.get('company_name', 'the contractor')
        specializations = contractor.get('specializations', 'general contracting')
        glazing_opportunities = contractor.get('glazing_opportunity_types', 'glazing services')
        city = contractor.get('city', 'Jacksonville')
        outreach_angle = contractor.get('outreach_angle', 'your projects')

        prompt = f"""Generate {num_scripts} cold call script{'s' if num_scripts > 1 else ''} for reaching this contractor about glazing services:

Contractor profile:
- Company: {company_name}
- Specialization: {specializations}
- Glazing opportunities: {glazing_opportunities}
- Location: {city}, Florida

Our glazing services:
- Frameless shower enclosures & glass shower doors
- Custom cabinet glass
- Glass tabletops & protective countertops
- Glass railings
- Commercial storefront systems
- Window/IGU replacement

Best outreach angle:
{outreach_angle}

Requirements:
- Opening line (15-20 seconds) - personalized to their work
- Value proposition specific to the glazing products they need
- 2-3 discovery questions to qualify their needs
- Handle common objections (already have supplier, not interested)
- Clear next step/close (send samples, schedule meeting, etc.)
- Natural conversational language (not scripted-sounding)
- Include [PAUSE] markers for listening to response
- Reference their location in Jacksonville/NE Florida area

Return as JSON:
{{
  {', '.join([f'"script_{i}": "full script text with [PAUSE] markers{" and different opening angle" if i > 1 else ""}"' for i in range(1, num_scripts + 1)])}
}}

Return ONLY the JSON object, no additional text."""

        try:
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
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost

            # Log usage to database
            self.db.log_api_usage(
                action_type="script_generation",
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=total_cost,
                contractor_id=contractor_id,
                success=True
            )

            print(f"API Usage - Script Gen: {input_tokens + output_tokens} tokens (${total_cost:.4f})")

            response_text = response.content[0].text.strip()

            # Clean markdown code blocks if present
            if response_text.startswith('```'):
                response_text = re.sub(r'^```json?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            scripts = json.loads(response_text)
            return scripts

        except json.JSONDecodeError as e:
            print(f"Failed to parse call scripts: {e}")
            print(f"Response: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"Error generating call scripts: {e}")
            return None

    def generate_all_outreach(self, contractor_id: int) -> Dict:
        """
        Generate all outreach materials for a contractor
        Returns status dict with success/failure and generated materials
        """
        result = {
            "success": False,
            "contractor_id": contractor_id,
            "message": "",
            "emails": None,
            "scripts": None
        }

        # Get contractor
        contractor = self.db.get_contractor_by_id(contractor_id)
        if not contractor:
            result["message"] = "Contractor not found"
            return result

        company_name = contractor.get("company_name", "Unknown")

        # Check if contractor is enriched
        if contractor.get('enrichment_status') != 'completed':
            result["message"] = f"{company_name} has not been enriched yet"
            return result

        print(f"Generating outreach materials for {company_name}...")

        # Generate email templates
        print("  - Generating email templates...")
        emails = self.generate_email_templates(contractor, contractor_id)
        if not emails:
            result["message"] = "Failed to generate email templates"
            return result

        # Generate call scripts
        print("  - Generating call scripts...")
        scripts = self.generate_call_scripts(contractor, contractor_id)
        if not scripts:
            result["message"] = "Failed to generate call scripts"
            return result

        # Save to database
        print("  - Saving to database...")
        saved_count = 0

        # Save 3 email templates
        for i in range(1, 4):
            email_key = f"email_{i}"
            if email_key in emails:
                email_data = emails[email_key]
                if self.db.save_outreach_material(
                    contractor_id=contractor_id,
                    material_type=email_key,
                    content=email_data.get('body', ''),
                    subject_line=email_data.get('subject', '')
                ):
                    saved_count += 1

        # Save 2 call scripts
        for i in range(1, 3):
            script_key = f"script_{i}"
            if script_key in scripts:
                if self.db.save_outreach_material(
                    contractor_id=contractor_id,
                    material_type=script_key,
                    content=scripts[script_key],
                    subject_line=None
                ):
                    saved_count += 1

        if saved_count == 5:
            result["success"] = True
            result["message"] = f"Generated and saved {saved_count} outreach materials for {company_name}"
            result["emails"] = emails
            result["scripts"] = scripts
            print(f"✓ Successfully generated all outreach materials for {company_name}")
        else:
            result["message"] = f"Only saved {saved_count}/5 materials"
            result["emails"] = emails
            result["scripts"] = scripts

        return result

    def get_outreach_materials(self, contractor_id: int) -> Dict:
        """
        Get all outreach materials for a contractor
        Returns dict organized by type
        """
        materials = self.db.get_outreach_materials(contractor_id)

        organized = {
            "emails": [],
            "scripts": []
        }

        for material in materials:
            if material['material_type'].startswith('email'):
                organized["emails"].append({
                    "id": material['id'],
                    "type": material['material_type'],
                    "subject": material.get('subject_line', ''),
                    "body": material.get('content', ''),
                    "is_edited": material.get('is_edited', False),
                    "date_generated": material.get('date_generated')
                })
            elif material['material_type'].startswith('script'):
                organized["scripts"].append({
                    "id": material['id'],
                    "type": material['material_type'],
                    "content": material.get('content', ''),
                    "is_edited": material.get('is_edited', False),
                    "date_generated": material.get('date_generated')
                })

        return organized

    def regenerate_outreach(self, contractor_id: int) -> Dict:
        """
        Delete existing outreach materials and generate new ones
        """
        # Delete existing materials
        try:
            self.db.client.table("outreach_materials").delete().eq("contractor_id", contractor_id).execute()
            print(f"Deleted existing outreach materials for contractor {contractor_id}")
        except Exception as e:
            print(f"Error deleting existing materials: {e}")

        # Generate new materials
        return self.generate_all_outreach(contractor_id)


# Helper function for easy usage
def generate_outreach(contractor_id: int) -> Dict:
    """
    Synchronous wrapper for generating outreach materials
    """
    generator = OutreachGenerator()
    result = generator.generate_all_outreach(contractor_id)
    return result


def get_contractor_outreach(contractor_id: int) -> Dict:
    """
    Get organized outreach materials for a contractor
    """
    generator = OutreachGenerator()
    return generator.get_outreach_materials(contractor_id)
