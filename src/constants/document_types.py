"""
Document Type Constants for SAFMC FMP Tracker
Defines all document categories and types for the comprehensive document system
"""

# Primary Document Types
class DocumentType:
    """Main document categories"""
    AMENDMENT = "amendment"
    REGULATORY_AMENDMENT = "regulatory_amendment"
    FRAMEWORK_AMENDMENT = "framework_amendment"
    SECRETARIAL_AMENDMENT = "secretarial_amendment"

    SCOPING_DOCUMENT = "scoping_document"
    PUBLIC_HEARING_DOC = "public_hearing_document"
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"
    ENVIRONMENTAL_IMPACT_STATEMENT = "environmental_impact_statement"

    MEETING_AGENDA = "meeting_agenda"
    MEETING_TRANSCRIPT = "meeting_transcript"
    MEETING_MINUTES = "meeting_minutes"
    BRIEFING_BOOK = "briefing_book"
    COMMITTEE_REPORT = "committee_report"

    PUBLIC_COMMENTS = "public_comments"
    COMMENT_SUMMARY = "comment_summary"

    FINAL_RULE = "final_rule"
    PROPOSED_RULE = "proposed_rule"
    INTERIM_RULE = "interim_rule"

    FMP_DOCUMENT = "fmp_document"
    REGULATORY_GUIDE = "regulatory_guide"
    FACT_SHEET = "fact_sheet"

    STOCK_ASSESSMENT_REPORT = "stock_assessment_report"
    SCIENTIFIC_REPORT = "scientific_report"

    OTHER = "other"

# Document Status
class DocumentStatus:
    """Document processing and lifecycle status"""
    DRAFT = "draft"
    SCOPING = "scoping"
    PUBLIC_HEARING = "public_hearing"
    SECRETARIAL_REVIEW = "secretarial_review"
    FINAL = "final"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"

# FMP Categories
class FMP:
    """Fishery Management Plan categories"""
    SNAPPER_GROUPER = "Snapper Grouper"
    DOLPHIN_WAHOO = "Dolphin Wahoo"
    COASTAL_MIGRATORY_PELAGICS = "Coastal Migratory Pelagics"
    GOLDEN_CRAB = "Golden Crab"
    SHRIMP = "Shrimp"
    SPINY_LOBSTER = "Spiny Lobster"
    CORAL = "Coral"
    SARGASSUM = "Sargassum"

    ALL = [
        SNAPPER_GROUPER,
        DOLPHIN_WAHOO,
        COASTAL_MIGRATORY_PELAGICS,
        GOLDEN_CRAB,
        SHRIMP,
        SPINY_LOBSTER,
        CORAL,
        SARGASSUM
    ]

# Source URLs for scraping
class DocumentSource:
    """Base URLs for document sources"""
    SAFMC_BASE = "https://safmc.net"
    BRIEFING_BOOKS = f"{SAFMC_BASE}/briefing-books/"
    AMENDMENTS = f"{SAFMC_BASE}/fishery-management/amendments-under-development/"
    COUNCIL_MEETINGS = f"{SAFMC_BASE}/council-meetings/"
    PUBLIC_HEARINGS = f"{SAFMC_BASE}/public-hearings-and-scoping/"
    PUBLIC_COMMENTS = f"{SAFMC_BASE}/public-comment/"

# Topic Categories for classification
class Topic:
    """Common topics for document categorization"""
    CATCH_LIMITS = "Catch Limits"
    QUOTAS = "Quotas"
    SIZE_LIMITS = "Size Limits"
    BAG_LIMITS = "Bag Limits"
    SEASON_DATES = "Season Dates"
    AREA_CLOSURES = "Area Closures"
    GEAR_RESTRICTIONS = "Gear Restrictions"
    PERMITTING = "Permitting"
    REPORTING_REQUIREMENTS = "Reporting Requirements"
    HABITAT_PROTECTION = "Habitat Protection"
    BYCATCH_REDUCTION = "Bycatch Reduction"
    ECOSYSTEM_MANAGEMENT = "Ecosystem Management"
    STOCK_REBUILDING = "Stock Rebuilding"
    ALLOCATION = "Allocation"
    LIMITED_ENTRY = "Limited Entry"
    FOR_HIRE_REGULATIONS = "For-Hire Regulations"
    RECREATIONAL_REGULATIONS = "Recreational Regulations"
    COMMERCIAL_REGULATIONS = "Commercial Regulations"

# Chunk Types for document segmentation
class ChunkType:
    """Types of document chunks for semantic search"""
    EXECUTIVE_SUMMARY = "executive_summary"
    PURPOSE_AND_NEED = "purpose_and_need"
    ALTERNATIVES = "alternatives"
    IMPACTS = "impacts"
    REGULATORY_TEXT = "regulatory_text"
    PUBLIC_COMMENT = "public_comment"
    APPENDIX = "appendix"
    TABLE = "table"
    FIGURE = "figure"
    GENERAL = "general"
