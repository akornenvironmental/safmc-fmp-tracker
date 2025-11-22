"""
Duplicate Detection Service
Identifies and helps merge duplicate contacts
"""

import logging
from sqlalchemy import func, or_, and_
from difflib import SequenceMatcher
from src.config.extensions import db
from src.models.contact import Contact
from src.models.comment import Comment

logger = logging.getLogger(__name__)


def similarity_score(a: str, b: str) -> float:
    """Calculate similarity between two strings"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def find_potential_duplicates(min_score: float = 0.8) -> list:
    """
    Find potential duplicate contacts based on name, email, and other fields
    Returns list of duplicate groups with confidence scores
    """
    duplicates = []
    processed_ids = set()

    try:
        contacts = Contact.query.all()
        contact_list = list(contacts)

        for i, contact_a in enumerate(contact_list):
            if contact_a.id in processed_ids:
                continue

            group = {
                'primary': contact_a.to_dict(),
                'primary_db_id': contact_a.id,
                'duplicates': [],
                'match_reasons': []
            }

            for j, contact_b in enumerate(contact_list):
                if i >= j or contact_b.id in processed_ids:
                    continue

                # Check for various match criteria
                match_score = 0
                reasons = []

                # Email match (strongest signal)
                if contact_a.email and contact_b.email:
                    email_sim = similarity_score(contact_a.email, contact_b.email)
                    if email_sim >= 0.95:
                        match_score += 0.5
                        reasons.append(f"Email match ({int(email_sim * 100)}%)")

                # Full name match
                if contact_a.full_name and contact_b.full_name:
                    name_sim = similarity_score(contact_a.full_name, contact_b.full_name)
                    if name_sim >= 0.85:
                        match_score += 0.3
                        reasons.append(f"Name match ({int(name_sim * 100)}%)")

                # Phone match
                if contact_a.phone and contact_b.phone:
                    # Normalize phone numbers (remove non-digits)
                    phone_a = ''.join(filter(str.isdigit, contact_a.phone))
                    phone_b = ''.join(filter(str.isdigit, contact_b.phone))
                    if len(phone_a) >= 7 and len(phone_b) >= 7:
                        if phone_a[-7:] == phone_b[-7:]:  # Match last 7 digits
                            match_score += 0.2
                            reasons.append("Phone match")

                # Location + name partial match
                if (contact_a.state and contact_b.state and
                    contact_a.state == contact_b.state and
                    contact_a.city and contact_b.city):
                    city_sim = similarity_score(contact_a.city, contact_b.city)
                    if city_sim >= 0.9:
                        # Check if last names match
                        if contact_a.last_name and contact_b.last_name:
                            last_name_sim = similarity_score(contact_a.last_name, contact_b.last_name)
                            if last_name_sim >= 0.9:
                                match_score += 0.15
                                reasons.append("Same city/state + similar last name")

                # Organization match with similar name
                if (contact_a.organization_id and contact_b.organization_id and
                    contact_a.organization_id == contact_b.organization_id):
                    if contact_a.full_name and contact_b.full_name:
                        name_sim = similarity_score(contact_a.full_name, contact_b.full_name)
                        if name_sim >= 0.7:
                            match_score += 0.1
                            reasons.append("Same organization + similar name")

                # If match score exceeds threshold, add to duplicates
                if match_score >= min_score:
                    group['duplicates'].append({
                        'contact': contact_b.to_dict(),
                        'db_id': contact_b.id,
                        'score': round(match_score, 2),
                        'reasons': reasons
                    })
                    processed_ids.add(contact_b.id)

            if group['duplicates']:
                # Sort duplicates by score
                group['duplicates'].sort(key=lambda x: x['score'], reverse=True)
                group['match_reasons'] = group['duplicates'][0]['reasons']
                duplicates.append(group)
                processed_ids.add(contact_a.id)

        # Sort groups by number of duplicates
        duplicates.sort(key=lambda x: len(x['duplicates']), reverse=True)

        logger.info(f"Found {len(duplicates)} potential duplicate groups")
        return duplicates

    except Exception as e:
        logger.error(f"Error finding duplicates: {e}")
        return []


def get_duplicate_stats() -> dict:
    """Get statistics about potential duplicates"""
    try:
        total_contacts = Contact.query.count()

        # Find exact email duplicates
        email_dupes = db.session.query(
            Contact.email,
            func.count(Contact.id).label('count')
        ).filter(
            Contact.email.isnot(None),
            Contact.email != ''
        ).group_by(Contact.email).having(func.count(Contact.id) > 1).all()

        # Find name + state duplicates
        name_state_dupes = db.session.query(
            Contact.full_name,
            Contact.state,
            func.count(Contact.id).label('count')
        ).filter(
            Contact.full_name.isnot(None),
            Contact.state.isnot(None)
        ).group_by(Contact.full_name, Contact.state).having(func.count(Contact.id) > 1).all()

        return {
            'total_contacts': total_contacts,
            'exact_email_duplicates': len(email_dupes),
            'email_duplicate_count': sum(d.count - 1 for d in email_dupes),
            'name_state_duplicates': len(name_state_dupes),
            'name_state_duplicate_count': sum(d.count - 1 for d in name_state_dupes),
            'estimated_duplicates': len(email_dupes) + len(name_state_dupes) // 2
        }

    except Exception as e:
        logger.error(f"Error getting duplicate stats: {e}")
        return {'error': str(e)}


def merge_contacts(primary_id: int, duplicate_ids: list) -> dict:
    """
    Merge duplicate contacts into the primary contact
    - Updates all comments to reference the primary contact
    - Consolidates engagement statistics
    - Deletes the duplicate contacts
    """
    try:
        primary = Contact.query.get(primary_id)
        if not primary:
            return {'success': False, 'error': 'Primary contact not found'}

        merged_count = 0
        comments_updated = 0

        for dup_id in duplicate_ids:
            duplicate = Contact.query.get(dup_id)
            if not duplicate or duplicate.id == primary.id:
                continue

            # Update comments to point to primary contact
            updated = Comment.query.filter_by(contact_id=duplicate.id).update(
                {'contact_id': primary.id},
                synchronize_session='fetch'
            )
            comments_updated += updated

            # Consolidate data - fill in any missing fields from duplicate
            if not primary.email and duplicate.email:
                primary.email = duplicate.email
            if not primary.phone and duplicate.phone:
                primary.phone = duplicate.phone
            if not primary.city and duplicate.city:
                primary.city = duplicate.city
            if not primary.state and duplicate.state:
                primary.state = duplicate.state
            if not primary.organization_id and duplicate.organization_id:
                primary.organization_id = duplicate.organization_id
            if not primary.title and duplicate.title:
                primary.title = duplicate.title
            if not primary.sector and duplicate.sector:
                primary.sector = duplicate.sector

            # Update engagement stats
            primary.total_comments = (primary.total_comments or 0) + (duplicate.total_comments or 0)
            primary.total_meetings_attended = (primary.total_meetings_attended or 0) + (duplicate.total_meetings_attended or 0)

            # Update engagement dates
            if duplicate.first_engagement_date:
                if not primary.first_engagement_date or duplicate.first_engagement_date < primary.first_engagement_date:
                    primary.first_engagement_date = duplicate.first_engagement_date
            if duplicate.last_engagement_date:
                if not primary.last_engagement_date or duplicate.last_engagement_date > primary.last_engagement_date:
                    primary.last_engagement_date = duplicate.last_engagement_date

            # Delete the duplicate
            db.session.delete(duplicate)
            merged_count += 1

        db.session.commit()

        logger.info(f"Merged {merged_count} contacts into {primary.contact_id}, updated {comments_updated} comments")

        return {
            'success': True,
            'merged_count': merged_count,
            'comments_updated': comments_updated,
            'primary_contact': primary.to_dict()
        }

    except Exception as e:
        logger.error(f"Error merging contacts: {e}")
        db.session.rollback()
        return {'success': False, 'error': str(e)}
