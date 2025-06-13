# app/models.py
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import INET, MACADDR, UUID
import uuid

# --- Lookup Tables (Normalized Data) ---
# These tables store static, reusable data to avoid redundancy
# and maintain data integrity.

class AssetTier(db.Model):
    __tablename__ = 'asset_tiers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    assets = db.relationship('Asset', backref='asset_tier', lazy=True)

    def __repr__(self):
        return f"<AssetTier {self.name}>"

class BusinessUnit(db.Model):
    __tablename__ = 'business_units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    assets = db.relationship('Asset', backref='business_unit', lazy=True)

    def __repr__(self):
        return f"<BusinessUnit {self.name}>"

class DataClassification(db.Model):
    __tablename__ = 'data_classifications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    assets = db.relationship('Asset', backref='data_classification', lazy=True)

    def __repr__(self):
        return f"<DataClassification {self.name}>"

class NetworkSegment(db.Model):
    __tablename__ = 'network_segments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    assets = db.relationship('Asset', backref='network_segment', lazy=True)

    def __repr__(self):
        return f"<NetworkSegment {self.name}>"

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    contact_email = db.Column(db.String(255))

    assets = db.relationship('Asset', backref='owner_team', lazy=True)

    def __repr__(self):
        return f"<Team {self.name}>"

class CVE(db.Model):
    __tablename__ = 'cves'
    cve_id = db.Column(db.String(50), primary_key=True) # Using CVE ID as PK
    description = db.Column(db.Text)
    cvss_score = db.Column(db.Numeric(3, 1))
    published_date = db.Column(db.Date)

    # Relationship to MisconfigurationRule (many-to-many through RuleCVE)
    rules = db.relationship('MisconfigurationRule', secondary='rule_cves', back_populates='cves')

    def __repr__(self):
        return f"<CVE {self.cve_id}>"

class CWE(db.Model):
    __tablename__ = 'cwes'
    cwe_id = db.Column(db.String(50), primary_key=True) # Using CWE ID as PK
    description = db.Column(db.Text)

    # Relationship to MisconfigurationRule (many-to-many through RuleCWE)
    rules = db.relationship('MisconfigurationRule', secondary='rule_cwes', back_populates='cwes')

    def __repr__(self):
        return f"<CWE {self.cwe_id}>"

class RemediationFix(db.Model):
    __tablename__ = 'remediation_fixes'
    fix_id = db.Column(db.String(255), primary_key=True) # Using OpenSCAP fix ID as PK
    fix_title = db.Column(db.String(500), nullable=False)
    fix_description = db.Column(db.Text, nullable=False)
    script_type = db.Column(db.String(50)) # e.g., 'bash', 'ansible', 'manual'
    script_content = db.Column(db.Text) # The actual script/commands
    expected_disruption = db.Column(db.String(50)) # e.g., 'Minimal', 'Service Restart', 'Outage'

    rules = db.relationship('MisconfigurationRule', backref='default_fix', lazy=True)
    # Specify primaryjoin and foreign_keys to resolve ambiguity due to multiple FKs in RemediationAction
    actions = db.relationship(
        "RemediationAction",
        backref="fix",
        primaryjoin="RemediationFix.fix_id==RemediationAction.fix_id",
        foreign_keys="RemediationAction.fix_id"
    )

    def __repr__(self):
        return f"<RemediationFix {self.fix_id}>"

class ThreatIntelligence(db.Model):
    __tablename__ = 'threat_intelligence'
    id = db.Column(db.Integer, primary_key=True)
    exploit_availability = db.Column(db.String(50)) # 'Public', 'Private', 'None', 'Unknown'
    active_exploitation_status = db.Column(db.Boolean, nullable=False, default=False)
    ransomware_association = db.Column(db.Boolean, nullable=False, default=False)
    threat_actor_targeting = db.Column(db.String(255)) # Specific threat actor groups
    source = db.Column(db.String(100)) # e.g., 'CISA KEV', 'OSINT'
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Link to CVEs (many-to-many) - a TI entry might relate to multiple CVEs
    cves = db.relationship('CVE', secondary='threat_intelligence_cves', backref='threat_intelligence')

    def __repr__(self):
        return f"<ThreatIntelligence {self.id} - Active Exploitation: {self.active_exploitation_status}>"

# --- Junction Tables for Many-to-Many Relationships ---

class RuleCVE(db.Model):
    __tablename__ = 'rule_cves'
    rule_id = db.Column(db.String(255), db.ForeignKey('misconfiguration_rules.rule_id'), primary_key=True)
    cve_id = db.Column(db.String(50), db.ForeignKey('cves.cve_id'), primary_key=True)

class RuleCWE(db.Model):
    __tablename__ = 'rule_cwes'
    rule_id = db.Column(db.String(255), db.ForeignKey('misconfiguration_rules.rule_id'), primary_key=True)
    cwe_id = db.Column(db.String(50), db.ForeignKey('cwes.cwe_id'), primary_key=True)

class MisconfigThreatIntel(db.Model):
    __tablename__ = 'misconfig_threat_intel'
    misconfig_id = db.Column(UUID(as_uuid=True), db.ForeignKey('asset_misconfigurations.id'), primary_key=True)
    ti_id = db.Column(db.Integer, db.ForeignKey('threat_intelligence.id'), primary_key=True)

class ThreatIntelligenceCVE(db.Model):
    __tablename__ = 'threat_intelligence_cves'
    ti_id = db.Column(db.Integer, db.ForeignKey('threat_intelligence.id'), primary_key=True)
    cve_id = db.Column(db.String(50), db.ForeignKey('cves.cve_id'), primary_key=True)


# --- Core Models ---

class Scan(db.Model):
    __tablename__ = 'scans'
    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(64), nullable=False) # e.g., 'OpenSCAP'
    target = db.Column(db.String(256)) # Can be IP, hostname, or scope description
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    
    scan_results = db.relationship('ScanResult', back_populates='scan', lazy=True) # Changed from 'results' for clarity

    def __repr__(self):
        return f"<Scan {self.tool_name} on {self.target} at {self.started_at}>"

class Asset(db.Model): # Renamed from 'Device' to be more encompassing
    __tablename__ = 'assets'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Using UUID for PK
    name = db.Column(db.String(128)) # Corresponds to hostname
    ip_address = db.Column(INET, unique=True, nullable=False)
    mac_address = db.Column(MACADDR)
    os_type = db.Column(db.String(100), nullable=False)
    os_version = db.Column(db.String(100), nullable=False)
    last_scanned_date = db.Column(db.DateTime)
    last_patch_date = db.Column(db.Date)
    uptime_seconds = db.Column(db.BigInteger) # For systems that track uptime
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Foreign Keys to Lookup Tables
    asset_tier_id = db.Column(db.Integer, db.ForeignKey('asset_tiers.id'))
    business_unit_id = db.Column(db.Integer, db.ForeignKey('business_units.id'))
    data_classification_id = db.Column(db.Integer, db.ForeignKey('data_classifications.id'))
    internet_facing = db.Column(db.Boolean, nullable=False, default=False)
    network_segment_id = db.Column(db.Integer, db.ForeignKey('network_segments.id'))
    owner_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    # Relationships
    credentials = db.relationship('Credential', back_populates='asset', cascade="all, delete-orphan")
    ports = db.relationship('Port', back_populates='asset', cascade="all, delete-orphan")
    routes = db.relationship('Route', back_populates='asset', cascade="all, delete-orphan")
    installed_applications = db.relationship('InstalledApplication', back_populates='asset', cascade="all, delete-orphan")
    security_controls = db.relationship('SecurityControl', back_populates='asset', cascade="all, delete-orphan")
    asset_misconfigurations = db.relationship('AssetMisconfiguration', back_populates='asset', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Asset {self.name} ({self.ip_address})>"

class Credential(db.Model):
    __tablename__ = 'credentials'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False) # Changed from device_id
    username = db.Column(db.String(64), nullable=False)
    # Password should be hashed and salted; for now, keeping as is for simplicity.
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', back_populates='credentials')

    def __repr__(self):
        return f"<Credential for {self.asset_id} - User: {self.username}>"

class Port(db.Model):
    __tablename__ = 'ports'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False) # Changed from device_id
    port_number = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    service_name = db.Column(db.String(128))
    state = db.Column(db.String(64)) # open, closed, filtered, etc.

    asset = db.relationship('Asset', back_populates='ports')

    def __repr__(self):
        return f"<Port {self.port_number}/{self.protocol} on {self.asset_id}>"

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False)
    destination = db.Column(INET)
    gateway = db.Column(INET)
    interface = db.Column(db.String(64))
    metric = db.Column(db.Integer)
    hop_number = db.Column(db.Integer, nullable=False)
    hop_ip = db.Column(INET, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    asset = db.relationship('Asset', back_populates='routes')

    def __repr__(self):
        return f"<Route hop {self.hop_number} ({self.hop_ip}) for {self.asset_id}>"

class InstalledApplication(db.Model):
    __tablename__ = 'installed_applications'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False)
    application_name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(100), nullable=False)

    asset = db.relationship('Asset', back_populates='installed_applications')

    def __repr__(self):
        return f"<App {self.application_name} v{self.version} on {self.asset_id}>"

class SecurityControl(db.Model):
    __tablename__ = 'security_controls'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False)
    control_type = db.Column(db.String(100), nullable=False) # e.g., 'WAF', 'IPS', 'EDR', 'MFA'
    control_status = db.Column(db.String(50)) # e.g., 'Active', 'Passive', 'Disabled'
    description = db.Column(db.Text)

    asset = db.relationship('Asset', back_populates='security_controls')

    def __repr__(self):
        return f"<Security Control {self.control_type} on {self.asset_id}>"

class ScanResult(db.Model):
    __tablename__ = 'scan_results'
    # This table now primarily links a scan to the detailed misconfigurations found.
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    # The 'device_id' is now 'asset_id' and represents the *target* of the scan,
    # rather than being directly tied to each scan result.
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False)
    
    # 'output' field from original ScanResult likely contained raw scan output.
    # This is now split into more granular misconfigurations, but a summary
    # or raw log can still be stored if needed.
    raw_scan_output_summary = db.Column(db.Text) # Optional: for summary/raw log
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scan = db.relationship('Scan', back_populates='scan_results')
    asset = db.relationship('Asset', backref='scan_results_for_asset', lazy=True)
    
    # Each ScanResult can have multiple misconfigurations found
    asset_misconfigurations = db.relationship('AssetMisconfiguration', back_populates='scan_result', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScanResult {self.id} for Asset {self.asset_id} from Scan {self.scan_id}>"

class MisconfigurationRule(db.Model):
    __tablename__ = 'misconfiguration_rules'
    rule_id = db.Column(db.String(255), primary_key=True) # OpenSCAP rule ID (e.g., 'xccdf_org.ssgproject.content_rule_...')
    rule_title = db.Column(db.String(500), nullable=False)
    rule_description = db.Column(db.Text, nullable=False)
    default_severity = db.Column(db.String(50), nullable=False) # 'High', 'Medium', 'Low' etc.
    impact_statement = db.Column(db.Text)

    # Default associated remediation fix (from SCAP content)
    default_remediation_fix_id = db.Column(db.String(255), db.ForeignKey('remediation_fixes.fix_id'))

    # Many-to-many relationships with CVEs and CWEs
    cves = db.relationship('CVE', secondary='rule_cves', back_populates='rules')
    cwes = db.relationship('CWE', secondary='rule_cwes', back_populates='rules')

    # One-to-many relationship with specific asset findings
    asset_misconfigurations = db.relationship('AssetMisconfiguration', back_populates='misconfig_rule', lazy=True)

    def __repr__(self):
        return f"<MisconfigRule {self.rule_id}>"

class AssetMisconfiguration(db.Model):
    __tablename__ = 'asset_misconfigurations'
    # This represents a specific finding of a misconfiguration on an asset during a scan.
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_result_id = db.Column(db.Integer, db.ForeignKey('scan_results.id'), nullable=False)
    asset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assets.id'), nullable=False)
    rule_id = db.Column(db.String(255), db.ForeignKey('misconfiguration_rules.rule_id'), nullable=False)
    
    # Specific details for this finding
    is_compliant = db.Column(db.Boolean, nullable=False) # True if compliant, False if misconfigured
    check_result_output = db.Column(db.Text) # The specific output from the check explaining the finding
    found_at = db.Column(db.DateTime, default=datetime.utcnow) # When this specific finding was detected

    scan_result = db.relationship('ScanResult', back_populates='asset_misconfigurations')
    asset = db.relationship('Asset', back_populates='asset_misconfigurations') # Bi-directional relationship
    misconfig_rule = db.relationship('MisconfigurationRule', back_populates='asset_misconfigurations')
    
    # Link to historical remediation actions for this specific finding
    remediation_actions = db.relationship('RemediationAction', back_populates='misconfiguration_finding', lazy=True, cascade="all, delete-orphan")

    # Many-to-many with ThreatIntelligence
    threat_intelligence_entries = db.relationship('ThreatIntelligence', secondary='misconfig_threat_intel', backref='misconfiguration_findings')

    def __repr__(self):
        return f"<AssetMisconfig {self.id} for {self.asset_id} Rule: {self.rule_id}>"

class RemediationAction(db.Model):
    __tablename__ = 'remediation_actions'
    # This table stores the actual actions taken, and crucially,
    # the human-assigned priority and outcome for AI training.
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    misconfig_id = db.Column(UUID(as_uuid=True), db.ForeignKey('asset_misconfigurations.id'), nullable=False)
    
    timestamp_initiated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    timestamp_completed = db.Column(db.DateTime)
    
    # The fix that was actually applied (can be a standard one or custom)
    applied_fix_id = db.Column(db.String(255), db.ForeignKey('remediation_fixes.fix_id'))
    custom_fix_description = db.Column(db.Text) # For non-standard fixes
    
    actual_priority_assigned = db.Column(db.String(50), nullable=False) # 'Critical', 'High', 'Medium', 'Low', 'Informational'
    priority_reasoning = db.Column(db.Text) # Textual explanation for the priority
    
    success_status = db.Column(db.String(50), nullable=False) # 'Success', 'Failure', 'Partial', 'Pending Re-scan'
    new_issues_introduced = db.Column(db.Boolean, nullable=False, default=False)
    human_override_reason = db.Column(db.Text) # Why humans deviated from default/AI suggestion

    # This is the main FK for the RemediationFix.actions relationship
    fix_id = db.Column(db.String(255), db.ForeignKey('remediation_fixes.fix_id'))

    # Fields to store AI's prediction for training/comparison
    ai_recommended_priority = db.Column(db.String(50))
    ai_recommended_fix_id = db.Column(db.String(255), db.ForeignKey('remediation_fixes.fix_id'))
    ai_confidence_score = db.Column(db.Numeric(5, 2)) # 0.00-1.00

    misconfiguration_finding = db.relationship('AssetMisconfiguration', back_populates='remediation_actions')
    ai_recommended_fix = db.relationship(
        'RemediationFix',
        foreign_keys=[ai_recommended_fix_id],
        backref='ai_recommendations',
        lazy=True
    )

    def __repr__(self):
        return f"<RemediationAction {self.id} for {self.misconfig_id} - Priority: {self.actual_priority_assigned}>"

# --- Lookup Tables (Normalized Data) ---
# AssetTier: Stores asset criticality tiers (e.g., Production, Development).
# BusinessUnit: Stores business units or departments that own assets.
# DataClassification: Stores data sensitivity levels (e.g., Public, Confidential).
# NetworkSegment: Stores network segmentation information for assets.
# Team: Stores teams responsible for assets.
# CVE: Stores Common Vulnerabilities and Exposures entries.
# CWE: Stores Common Weakness Enumeration entries.

# --- Core Models ---
# RemediationFix: Stores remediation scripts/fixes for misconfigurations.
# ThreatIntelligence: Stores threat intelligence data (e.g., exploit status, ransomware association).
# Scan: Stores information about each scan performed (tool, target, timestamps).
# Asset: Stores information about each asset (host/device) in the environment.
# Credential: Stores credentials associated with assets.
# Port: Stores open ports/services for each asset.
# Route: Stores network routes for each asset.
# InstalledApplication: Stores installed applications on each asset.
# SecurityControl: Stores security controls deployed on each asset.
# ScanResult: Stores results of each scan, linking to assets and findings.
# MisconfigurationRule: Stores rules for detecting misconfigurations (with links to CVEs/CWEs).
# AssetMisconfiguration: Stores specific misconfiguration findings for assets during scans.
# RemediationAction: Stores actions taken to remediate misconfigurations, including human and AI decisions.

# --- Junction Tables for Many-to-Many Relationships ---
# RuleCVE: Associates misconfiguration rules with CVEs (many-to-many).
# RuleCWE: Associates misconfiguration rules with CWEs (many-to-many).
# MisconfigThreatIntel: Associates asset misconfigurations with threat intelligence entries (many-to-many).
# ThreatIntelligenceCVE: Associates threat intelligence entries with CVEs (many-to-many).