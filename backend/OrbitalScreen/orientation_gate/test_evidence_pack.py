"""
Unit Tests for Evidence Pack Schema and Validation

Mission: Scaffold Cockpit Launch Protocol
Commander: Orbital
Timestamp: 2025-01-23 16:20:00 UTC
"""

import json
import hashlib
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


class EvidencePackValidator:
    """Validates evidence packs against the schema"""
    
    def __init__(self, schema_path: str = "index.json"):
        self.schema_path = Path(__file__).parent / schema_path
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the evidence pack schema"""
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def validate_structure(self, evidence_pack: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate evidence pack structure against schema
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        schema = self.schema['evidence_pack_schema']
        
        required = schema.get('required', [])
        for field in required:
            if field not in evidence_pack:
                errors.append(f"Missing required field: {field}")
        
        if 'agent_id' in evidence_pack:
            agent_id = evidence_pack['agent_id']
            if not agent_id.startswith('agent_'):
                errors.append(f"Invalid agent_id format: {agent_id}")
        
        if 'evidence_entries' in evidence_pack:
            entries = evidence_pack['evidence_entries']
            if not isinstance(entries, list):
                errors.append("evidence_entries must be an array")
            elif len(entries) < 1:
                errors.append("evidence_entries must have at least 1 entry")
            else:
                for i, entry in enumerate(entries):
                    entry_errors = self._validate_entry(entry, i)
                    errors.extend(entry_errors)
        
        if 'verification' in evidence_pack:
            verification = evidence_pack['verification']
            if 'pack_hash' not in verification:
                errors.append("verification.pack_hash is required")
            if 'entry_count' not in verification:
                errors.append("verification.entry_count is required")
            elif verification['entry_count'] != len(evidence_pack.get('evidence_entries', [])):
                errors.append("verification.entry_count does not match actual entry count")
        
        return (len(errors) == 0, errors)
    
    def _validate_entry(self, entry: Dict[str, Any], index: int) -> list[str]:
        """Validate a single evidence entry"""
        errors = []
        required_fields = ['entry_id', 'entry_type', 'timestamp', 'description', 'verification_hash']
        
        for field in required_fields:
            if field not in entry:
                errors.append(f"Entry {index}: Missing required field '{field}'")
        
        valid_types = [
            'action_log', 'decision_record', 'communication_record',
            'task_documentation', 'error_report', 'checkpoint', 'handoff_material'
        ]
        if 'entry_type' in entry and entry['entry_type'] not in valid_types:
            errors.append(f"Entry {index}: Invalid entry_type '{entry['entry_type']}'")
        
        if 'verification_hash' in entry:
            hash_val = entry['verification_hash']
            if not isinstance(hash_val, str) or len(hash_val) != 64:
                errors.append(f"Entry {index}: verification_hash must be 64 hex characters")
        
        return errors
    
    def calculate_checksum(self, evidence_pack: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum of evidence pack"""
        pack_copy = evidence_pack.copy()
        if 'verification' in pack_copy:
            pack_copy = {k: v for k, v in pack_copy.items() if k != 'verification'}
        
        json_str = json.dumps(pack_copy, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def verify_integrity(self, evidence_pack: Dict[str, Any]) -> bool:
        """Verify the integrity of an evidence pack using its checksum"""
        if 'verification' not in evidence_pack:
            return False
        
        stored_hash = evidence_pack['verification'].get('pack_hash')
        if not stored_hash:
            return False
        
        calculated_hash = self.calculate_checksum(evidence_pack)
        return stored_hash == calculated_hash


class TestEvidencePackSchema(unittest.TestCase):
    """Test cases for Evidence Pack schema validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = EvidencePackValidator()
        self.sample_pack_path = Path(__file__).parent / "evidence_pack.sample.json"
        
        with open(self.sample_pack_path, 'r') as f:
            self.sample_pack = json.load(f)
    
    def test_schema_loads(self):
        """Test that the schema file loads correctly"""
        self.assertIsNotNone(self.validator.schema)
        self.assertIn('evidence_pack_schema', self.validator.schema)
    
    def test_sample_pack_loads(self):
        """Test that the sample evidence pack loads correctly"""
        self.assertIsNotNone(self.sample_pack)
        self.assertIn('agent_id', self.sample_pack)
    
    def test_required_fields_present(self):
        """Test that all required fields are present in sample pack"""
        required_fields = ['agent_id', 'agent_name', 'mission_id', 'timestamp', 'evidence_entries']
        for field in required_fields:
            self.assertIn(field, self.sample_pack, f"Missing required field: {field}")
    
    def test_agent_id_format(self):
        """Test that agent_id follows the correct format"""
        agent_id = self.sample_pack['agent_id']
        self.assertTrue(agent_id.startswith('agent_'), "agent_id must start with 'agent_'")
    
    def test_evidence_entries_not_empty(self):
        """Test that evidence_entries array is not empty"""
        entries = self.sample_pack['evidence_entries']
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0, "evidence_entries must have at least one entry")
    
    def test_evidence_entry_structure(self):
        """Test that each evidence entry has required fields"""
        required_fields = ['entry_id', 'entry_type', 'timestamp', 'description', 'verification_hash']
        
        for i, entry in enumerate(self.sample_pack['evidence_entries']):
            for field in required_fields:
                self.assertIn(field, entry, f"Entry {i} missing field: {field}")
    
    def test_evidence_entry_types_valid(self):
        """Test that all entry types are valid"""
        valid_types = [
            'action_log', 'decision_record', 'communication_record',
            'task_documentation', 'error_report', 'checkpoint', 'handoff_material'
        ]
        
        for entry in self.sample_pack['evidence_entries']:
            self.assertIn(entry['entry_type'], valid_types,
                         f"Invalid entry_type: {entry['entry_type']}")
    
    def test_verification_section_present(self):
        """Test that verification section is present"""
        self.assertIn('verification', self.sample_pack)
        verification = self.sample_pack['verification']
        self.assertIn('pack_hash', verification)
        self.assertIn('entry_count', verification)
    
    def test_entry_count_matches(self):
        """Test that verification.entry_count matches actual count"""
        actual_count = len(self.sample_pack['evidence_entries'])
        declared_count = self.sample_pack['verification']['entry_count']
        self.assertEqual(actual_count, declared_count,
                        "entry_count mismatch")
    
    def test_verification_hash_format(self):
        """Test that verification hashes are 64 hex characters"""
        for entry in self.sample_pack['evidence_entries']:
            hash_val = entry['verification_hash']
            self.assertEqual(len(hash_val), 64,
                           f"verification_hash must be 64 characters: {entry['entry_id']}")
    
    def test_timestamp_format(self):
        """Test that timestamps are in ISO 8601 format"""
        timestamp = self.sample_pack['timestamp']
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.fail(f"Invalid timestamp format: {timestamp}")
    
    def test_validator_structure_check(self):
        """Test the validator's structure checking"""
        is_valid, errors = self.validator.validate_structure(self.sample_pack)
        if not is_valid:
            self.fail(f"Sample pack validation failed: {errors}")
    
    def test_checksum_calculation(self):
        """Test that checksum calculation is reproducible"""
        checksum1 = self.validator.calculate_checksum(self.sample_pack)
        checksum2 = self.validator.calculate_checksum(self.sample_pack)
        self.assertEqual(checksum1, checksum2, "Checksum calculation not reproducible")
    
    def test_checksum_format(self):
        """Test that calculated checksum is valid SHA256"""
        checksum = self.validator.calculate_checksum(self.sample_pack)
        self.assertEqual(len(checksum), 64, "SHA256 hash must be 64 hex characters")
        self.assertTrue(all(c in '0123456789abcdef' for c in checksum),
                       "Checksum must be hexadecimal")
    
    def test_missing_required_field(self):
        """Test validation fails when required field is missing"""
        invalid_pack = self.sample_pack.copy()
        del invalid_pack['agent_id']
        
        is_valid, errors = self.validator.validate_structure(invalid_pack)
        self.assertFalse(is_valid)
        self.assertTrue(any('agent_id' in err for err in errors))
    
    def test_invalid_agent_id_format(self):
        """Test validation fails for invalid agent_id format"""
        invalid_pack = self.sample_pack.copy()
        invalid_pack['agent_id'] = 'invalid_format'
        
        is_valid, errors = self.validator.validate_structure(invalid_pack)
        self.assertFalse(is_valid)
        self.assertTrue(any('agent_id' in err for err in errors))
    
    def test_empty_evidence_entries(self):
        """Test validation fails for empty evidence_entries"""
        invalid_pack = self.sample_pack.copy()
        invalid_pack['evidence_entries'] = []
        
        is_valid, errors = self.validator.validate_structure(invalid_pack)
        self.assertFalse(is_valid)
        self.assertTrue(any('at least 1 entry' in err for err in errors))
    
    def test_invalid_entry_type(self):
        """Test validation fails for invalid entry_type"""
        invalid_pack = self.sample_pack.copy()
        invalid_pack['evidence_entries'][0]['entry_type'] = 'invalid_type'
        
        is_valid, errors = self.validator.validate_structure(invalid_pack)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid entry_type' in err for err in errors))
    
    def test_metadata_section(self):
        """Test that metadata section contains expected fields"""
        self.assertIn('metadata', self.sample_pack)
        metadata = self.sample_pack['metadata']
        self.assertIn('clearance_level', metadata)
        self.assertIn('mission_phase', metadata)


class TestEvidencePackReproducibility(unittest.TestCase):
    """Test cases for Evidence Pack reproducibility"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = EvidencePackValidator()
    
    def test_create_minimal_pack(self):
        """Test creating a minimal valid evidence pack"""
        minimal_pack = {
            "agent_id": "agent_test",
            "agent_name": "Test Agent",
            "mission_id": "test_mission",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_entries": [
                {
                    "entry_id": "test_001",
                    "entry_type": "action_log",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "description": "Test action",
                    "verification_hash": "0" * 64
                }
            ],
            "verification": {
                "pack_hash": "0" * 64,
                "entry_count": 1
            }
        }
        
        is_valid, errors = self.validator.validate_structure(minimal_pack)
        self.assertTrue(is_valid, f"Minimal pack validation failed: {errors}")
    
    def test_checksum_reproducibility(self):
        """Test that the same pack produces the same checksum"""
        pack = {
            "agent_id": "agent_test",
            "agent_name": "Test",
            "mission_id": "test",
            "timestamp": "2025-01-23T16:20:00Z",
            "evidence_entries": [
                {
                    "entry_id": "e1",
                    "entry_type": "action_log",
                    "timestamp": "2025-01-23T16:20:00Z",
                    "description": "Test",
                    "verification_hash": "0" * 64
                }
            ]
        }
        
        checksums = [self.validator.calculate_checksum(pack) for _ in range(10)]
        self.assertEqual(len(set(checksums)), 1, "Checksum not reproducible")


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestEvidencePackSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestEvidencePackReproducibility))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 80)
    print("Evidence Pack Unit Tests")
    print("Mission: Scaffold Cockpit Launch Protocol")
    print("=" * 80)
    print()
    
    result = run_tests()
    
    print()
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 80)
    
    exit(0 if result.wasSuccessful() else 1)
