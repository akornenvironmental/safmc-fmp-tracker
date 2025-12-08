"""
Entity Matcher - Fuzzy matching for contacts and organizations
Uses Levenshtein distance to find and deduplicate entities
"""

import re
import hashlib
from typing import Optional, Tuple
from rapidfuzz import fuzz
from datetime import datetime

from src.config.extensions import db
from src.models.contact import Contact
from src.models.organization import Organization
from src.models.action import Action

import logging
logger = logging.getLogger(__name__)

# Matching thresholds
CONTACT_MATCH_THRESHOLD = 85  # 85% similarity for contact matching
ORG_MATCH_THRESHOLD = 85  # 85% similarity for organization matching


def normalize_name(name: str) -> str:
    """Normalize a name for fuzzy matching"""
    if not name:
        return ''

    # Convert to lowercase
    normalized = name.lower()

    # Remove common business suffixes
    suffixes = [
        'inc', 'inc.', 'incorporated', 'llc', 'l.l.c.', 'ltd', 'ltd.',
        'limited', 'corp', 'corp.', 'corporation', 'co', 'co.',
        'association', 'assoc', 'assoc.', 'org', 'organization'
    ]
    for suffix in suffixes:
        pattern = rf'\b{re.escape(suffix)}\b'
        normalized = re.sub(pattern, '', normalized)

    # Remove punctuation except spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)

    # Remove extra whitespace
    normalized = ' '.join(normalized.split())

    return normalized.strip()


def generate_contact_id(full_name: str, email: str) -> str:
    """Generate a unique contact ID from name and email"""
    key = f"{normalize_name(full_name or '')}_{(email or '').lower()}".encode('utf-8')
    return f"CONT-{hashlib.md5(key).hexdigest()[:12].upper()}"


def generate_org_id(org_name: str) -> str:
    """Generate a unique organization ID from name"""
    key = normalize_name(org_name or '').encode('utf-8')
    return f"ORG-{hashlib.md5(key).hexdigest()[:12].upper()}"


def find_or_create_contact(
    full_name: str,
    email: str,
    city: str = None,
    state: str = None,
    sector: str = None,
    data_source: str = None
) -> Optional[Contact]:
    """
    Find existing contact using fuzzy matching or create new one

    Matching strategy:
    1. Exact email match (if email provided)
    2. Fuzzy name match in same state (if state provided)
    3. Fuzzy name match globally
    4. Create new if no match
    """
    if not full_name and not email:
        return None

    # Try exact email match first
    if email:
        contact = Contact.query.filter(
            db.func.lower(Contact.email) == email.lower()
        ).first()
        if contact:
            logger.debug(f"Found exact email match: {contact.contact_id}")
            return contact

    # Try fuzzy name matching
    if full_name:
        normalized_input = normalize_name(full_name)

        # First try in same state
        if state:
            candidates = Contact.query.filter(
                Contact.state == state
            ).limit(100).all()

            for candidate in candidates:
                if not candidate.full_name:
                    continue

                similarity = fuzz.ratio(normalized_input, normalize_name(candidate.full_name))
                if similarity >= CONTACT_MATCH_THRESHOLD:
                    logger.debug(f"Found fuzzy match (state): {candidate.contact_id} (similarity: {similarity}%)")
                    return candidate

        # Then try globally (limit to avoid performance issues)
        candidates = Contact.query.limit(500).all()
        for candidate in candidates:
            if not candidate.full_name:
                continue

            similarity = fuzz.ratio(normalized_input, normalize_name(candidate.full_name))
            if similarity >= CONTACT_MATCH_THRESHOLD:
                # If we found a match, also check email if both have it
                if email and candidate.email:
                    if email.lower() != candidate.email.lower():
                        # Different emails, probably different people
                        continue

                logger.debug(f"Found fuzzy match (global): {candidate.contact_id} (similarity: {similarity}%)")
                return candidate

    # No match found, create new contact
    contact_id = generate_contact_id(full_name, email)

    # Split name into first and last
    first_name = ''
    last_name = ''
    if full_name:
        parts = full_name.strip().split()
        if len(parts) > 0:
            first_name = parts[0]
        if len(parts) > 1:
            last_name = ' '.join(parts[1:])

    contact = Contact(
        contact_id=contact_id,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        email=email,
        city=city,
        state=state,
        sector=sector,
        data_source=data_source,
        total_comments=0,
        first_engagement_date=datetime.utcnow(),
        last_engagement_date=datetime.utcnow()
    )

    db.session.add(contact)
    logger.info(f"Created new contact: {contact_id} - {full_name}")

    return contact


def find_or_create_organization(
    org_name: str,
    state: str = None,
    org_type: str = None,
    data_source: str = None
) -> Optional[Organization]:
    """
    Find existing organization using fuzzy matching or create new one

    Matching strategy:
    1. Exact name match
    2. Fuzzy name match in same state
    3. Fuzzy name match globally
    4. Create new if no match
    """
    if not org_name or not org_name.strip():
        return None

    # Try exact name match first
    org = Organization.query.filter(
        db.func.lower(Organization.name) == org_name.lower()
    ).first()
    if org:
        logger.debug(f"Found exact name match: {org.org_id}")
        return org

    # Try fuzzy matching
    normalized_input = normalize_name(org_name)

    # First try in same state
    if state:
        candidates = Organization.query.filter(
            Organization.state == state
        ).limit(100).all()

        for candidate in candidates:
            similarity = fuzz.ratio(normalized_input, candidate.name_normalized or '')
            if similarity >= ORG_MATCH_THRESHOLD:
                logger.debug(f"Found fuzzy match (state): {candidate.org_id} (similarity: {similarity}%)")
                return candidate

    # Then try globally
    candidates = Organization.query.limit(500).all()
    for candidate in candidates:
        similarity = fuzz.ratio(normalized_input, candidate.name_normalized or '')
        if similarity >= ORG_MATCH_THRESHOLD:
            logger.debug(f"Found fuzzy match (global): {candidate.org_id} (similarity: {similarity}%)")
            return candidate

    # No match found, create new organization
    org_id = generate_org_id(org_name)

    org = Organization(
        org_id=org_id,
        name=org_name,
        name_normalized=normalized_input,
        state=state,
        org_type=org_type,
        data_source=data_source,
        total_comments=0,
        first_engagement_date=datetime.utcnow(),
        last_engagement_date=datetime.utcnow()
    )

    db.session.add(org)
    logger.info(f"Created new organization: {org_id} - {org_name}")

    return org


def _extract_fmp_from_title(title: str) -> Optional[str]:
    """
    Extract FMP from amendment title

    Examples:
        "Snapper Grouper Amendment 56" -> "Snapper Grouper"
        "Coral Amendment 11 / Shrimp Amendment 12" -> "Multiple FMPs"
        "Dolphin Wahoo Regulatory Amendment 3" -> "Dolphin Wahoo"
        "Comprehensive Amendment 37 - Modifications to Fishing Year" -> "Multiple FMPs"
    """
    if not title:
        return None

    title_lower = title.lower()

    # FMP keywords (ordered by specificity to avoid false matches)
    fmp_patterns = [
        ('Snapper Grouper', ['snapper-grouper', 'snapper grouper']),
        ('Dolphin Wahoo', ['dolphin-wahoo', 'dolphin wahoo', 'dolphin/wahoo']),
        ('Coastal Migratory Pelagics', ['coastal migratory pelagic', 'cmp', 'mackerel', 'cobia']),
        ('Golden Crab', ['golden crab']),
        ('Shrimp', ['shrimp']),
        ('Spiny Lobster', ['spiny lobster', 'lobster']),
        ('Coral', ['coral']),
        ('Sargassum', ['sargassum'])
    ]

    # Check if this is a comprehensive/omnibus amendment
    if 'comprehensive' in title_lower or 'omnibus' in title_lower:
        # Count how many FMPs are mentioned
        matched_fmps = []
        for fmp_name, keywords in fmp_patterns:
            for keyword in keywords:
                if keyword in title_lower:
                    if fmp_name not in matched_fmps:
                        matched_fmps.append(fmp_name)
                    break

        # If multiple FMPs or no specific FMP, return "Multiple FMPs"
        if len(matched_fmps) > 1:
            return 'Multiple FMPs'
        elif len(matched_fmps) == 1:
            return matched_fmps[0]
        else:
            # Comprehensive but no specific FMP mentioned - likely affects multiple
            return 'Multiple FMPs'

    # For non-comprehensive amendments, return first match
    for fmp_name, keywords in fmp_patterns:
        for keyword in keywords:
            if keyword in title_lower:
                return fmp_name

    return None


def find_or_create_action(
    amendment_title: str,
    description: str = None,
    phase: str = None,
    data_source: str = None
) -> Optional[Action]:
    """
    Find existing action or create new one based on amendment metadata

    Tries to match by title fuzzy matching
    """
    if not amendment_title or not amendment_title.strip():
        return None

    # Try exact title match
    action = Action.query.filter(
        db.func.lower(Action.title) == amendment_title.lower()
    ).first()
    if action:
        logger.debug(f"Found exact action match: {action.action_id}")
        return action

    # Try fuzzy matching on title
    normalized_input = normalize_name(amendment_title)
    candidates = Action.query.limit(100).all()

    for candidate in candidates:
        if not candidate.title:
            continue

        similarity = fuzz.ratio(normalized_input, normalize_name(candidate.title))
        if similarity >= 85:  # 85% threshold for actions
            logger.debug(f"Found fuzzy action match: {candidate.action_id} (similarity: {similarity}%)")
            return candidate

    # No match found, create new action
    # Generate action_id from title
    # Convert title like "Comprehensive Amendment Coral 11 and Shrimp 12" to "coral-11-shrimp-12"
    action_id_base = re.sub(r'[^\w\s-]', '', amendment_title.lower())
    action_id_base = re.sub(r'\s+', '-', action_id_base)
    # Remove common words
    for word in ['comprehensive', 'amendment', 'and', 'the', 'a', 'an']:
        action_id_base = action_id_base.replace(f'-{word}-', '-')
        action_id_base = action_id_base.replace(f'{word}-', '')
        action_id_base = action_id_base.replace(f'-{word}', '')
    action_id_base = action_id_base.strip('-')[:50]  # Limit length

    # Extract FMP from title
    fmp = _extract_fmp_from_title(amendment_title)
    logger.info(f"Extracted FMP '{fmp}' from title: {amendment_title}")

    action = Action(
        action_id=action_id_base,
        title=amendment_title,
        description=description,
        fmp=fmp,  # Add FMP field
        status=phase or 'Public Comment',
        type='Amendment',
        start_date=datetime.utcnow()
    )

    db.session.add(action)
    logger.info(f"Created new action: {action_id_base} - {amendment_title} (FMP: {fmp})")

    return action
