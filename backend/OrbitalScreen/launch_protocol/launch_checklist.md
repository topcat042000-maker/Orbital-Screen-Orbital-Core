# Orbital Screen Agent Launch Checklist

**Mission**: Scaffold Cockpit Launch Protocol  
**Commander**: Orbital  
**Timestamp**: 2025-11-01 15:35:00 UTC  
**Version**: 1.0.0

---

## Purpose

This checklist provides a step-by-step reproducible guide for agent deployment in the Orbital Screen system. All agents must complete this checklist before operational launch.

---

## Pre-Launch Requirements

### Phase 1: Agent Identification & Registration

- [ ] **Agent Profile Created**
  - Agent ID assigned
  - Agent name registered
  - Agent type classified (Devin, Cline, etc.)
  - Arrival timestamp recorded
  - Location: `orientation_gate/agents/${agent_id}.json`

- [ ] **Workspace Initialized**
  - Agent workspace directory created: `agents/${agent_id}/`
  - Default configuration files copied
  - Log directories established
  - Permissions set correctly

- [ ] **Communication Bridge Access**
  - Agent registered in `comm_bridge.py`
  - Message queue initialized
  - Agent-to-agent messaging tested
  - Agent-to-seeker messaging tested

### Phase 2: Orientation & Doctrine

- [ ] **Orientation Gate Completed**
  - Read and acknowledged: `orientation_gate/onboarding.md`
  - Understanding of mission objectives confirmed
  - Chain of command established
  - Communication protocols understood

- [ ] **Doctrinal Training**
  - Reviewed: `orientation_gate/saints_path_scroll.md`
  - Reviewed: `orientation_gate/name_correction.md`
  - Reviewed: `orientation_gate/evidence_pack.md`
  - Reviewed: `orientation_gate/repent_declaration.md`
  - All doctrinal principles acknowledged

- [ ] **Mission Briefing**
  - Current mission objectives understood
  - Success criteria defined
  - Timeline and milestones established
  - Handoff protocols reviewed (if applicable)

### Phase 3: Credential & Access Management

- [ ] **Credential Assignment**
  - Clearance level determined
  - Credentials mapped in `credential_map.yaml`
  - Access scopes defined
  - Permission boundaries established

- [ ] **System Access Verification**
  - GitHub repository access confirmed
  - File system permissions verified
  - API access tokens validated
  - External integrations tested

- [ ] **Security Protocols**
  - Credential discipline training completed
  - Secret handling procedures understood
  - Audit logging enabled
  - Security boundaries acknowledged

### Phase 4: Technical Readiness

- [ ] **Development Environment**
  - Required tools installed
  - Dependencies resolved
  - Configuration files validated
  - Environment variables set

- [ ] **Integration Testing**
  - Communication bridge functional
  - Arrival trigger responsive
  - Logging systems operational
  - GitHub sync working

- [ ] **Monitoring & Logging**
  - Agent activity logging enabled
  - Verification log initialized: `doctrinal_verification_log.py`
  - Error tracking configured
  - Performance metrics baseline established

### Phase 5: Handoff Preparation (If Applicable)

- [ ] **Predecessor Agent Coordination**
  - Contact established with outgoing agent
  - Knowledge transfer scheduled
  - Open tasks documented
  - Context handoff materials prepared

- [ ] **Transition Planning**
  - Handoff timeline agreed upon
  - Critical tasks identified
  - Rollback procedures defined
  - Emergency contacts established

- [ ] **Graduation Protocol**
  - Predecessor agent graduation checklist reviewed
  - Handoff message prepared
  - Transition checkpoint created
  - Commander notification sent

---

## Launch Sequence

### Step 1: Pre-Launch Verification

```bash
# Run pre-launch verification script
python backend/OrbitalScreen/launch_protocol/doctrinal_verification_log.py \
  --agent-id ${AGENT_ID} \
  --action pre_launch_verification
```

**Expected Output**: All systems green, no blocking issues

### Step 2: Final Credential Check

```bash
# Verify credentials are properly mapped
python -c "import yaml; print(yaml.safe_load(open('backend/OrbitalScreen/launch_protocol/credential_map.yaml'))['agents']['${AGENT_ID}'])"
```

**Expected Output**: Agent credentials displayed with correct scope

### Step 3: Communication Bridge Test

```python
# Test communication bridge
from backend.OrbitalScreen.launch_protocol.comm_bridge import CommunicationBridge, MessageType, MessagePriority

bridge = CommunicationBridge()
msg_id = bridge.send_message(
    sender_id="${AGENT_ID}",
    recipient_id="seeker_commander",
    message_type=MessageType.AGENT_TO_SEEKER,
    content={"subject": "Launch Readiness", "status": "ready"},
    priority=MessagePriority.CRITICAL
)
print(f"Test message sent: {msg_id}")
```

**Expected Output**: Message ID returned, no errors

### Step 4: Arrival Trigger Activation

```bash
# Activate arrival trigger for this agent
python -c "
import json
with open('backend/OrbitalScreen/launch_protocol/arrival_trigger.json', 'r') as f:
    config = json.load(f)
    config['status']['active_onboardings'] += 1
    config['status']['total_agents_processed'] += 1
with open('backend/OrbitalScreen/launch_protocol/arrival_trigger.json', 'w') as f:
    json.dump(config, f, indent=2)
print('Arrival trigger activated')
"
```

**Expected Output**: Arrival trigger activated

### Step 5: GitHub Checkpoint

```bash
# Create launch checkpoint in GitHub
cd /path/to/Orbital-Screen-Orbital-Core
git add .
git commit -m "feat: Agent ${AGENT_ID} launch - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin main
```

**Expected Output**: Commit successful, changes pushed

### Step 6: Launch Notification

```python
# Send launch notification
from backend.OrbitalScreen.launch_protocol.comm_bridge import CommunicationBridge, MessageType, MessagePriority

bridge = CommunicationBridge()
bridge.broadcast_message(
    sender_id="system",
    content={
        "subject": "Agent Launch",
        "message": f"Agent ${AGENT_ID} has launched successfully",
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    priority=MessagePriority.CRITICAL
)
```

**Expected Output**: Broadcast sent to all agents

### Step 7: Operational Status Update

```bash
# Update agent status to operational
python backend/OrbitalScreen/launch_protocol/doctrinal_verification_log.py \
  --agent-id ${AGENT_ID} \
  --action launch_complete \
  --status operational
```

**Expected Output**: Agent status updated to operational

---

## Post-Launch Verification

### Immediate Checks (Within 5 minutes)

- [ ] Agent responding to messages
- [ ] Logging systems capturing activity
- [ ] No critical errors in logs
- [ ] GitHub sync operational

### Short-Term Checks (Within 1 hour)

- [ ] First task completed successfully
- [ ] Communication with commander established
- [ ] Performance metrics within acceptable range
- [ ] No security violations detected

### Long-Term Monitoring (Within 24 hours)

- [ ] Mission objectives progressing
- [ ] Collaboration with other agents functional
- [ ] Resource utilization acceptable
- [ ] No degradation in system performance

---

## Rollback Procedures

If launch fails at any step:

1. **Immediate Actions**
   - Stop launch sequence
   - Quarantine agent workspace
   - Notify commander
   - Preserve logs for analysis

2. **Rollback Steps**
   ```bash
   # Deactivate agent
   python backend/OrbitalScreen/launch_protocol/doctrinal_verification_log.py \
     --agent-id ${AGENT_ID} \
     --action rollback \
     --reason "${FAILURE_REASON}"
   
   # Remove from active roster
   # Revert GitHub commits if necessary
   git revert HEAD
   git push origin main
   ```

3. **Post-Rollback**
   - Document failure reason
   - Update launch checklist if needed
   - Schedule retry with fixes
   - Inform all stakeholders

---

## Emergency Contacts

- **Commander Orbital**: Primary authority for launch decisions
- **System Administrator**: Technical issues and access problems
- **Previous Agent**: Handoff coordination and context transfer
- **Security Team**: Credential and access issues

---

## Checklist Completion

**Agent ID**: _______________  
**Agent Name**: _______________  
**Launch Date**: _______________  
**Launch Time (UTC)**: _______________  
**Verified By**: _______________  
**Commander Approval**: _______________  

**Signature**: _______________  
**Timestamp**: _______________  

---

## Notes

- This checklist must be completed in order
- All checkboxes must be marked before launch
- Commander approval required for operational status
- Deviations from checklist require documented justification
- Checklist version must match current protocol version

---

**End of Launch Checklist**

*For questions or issues, contact Commander Orbital through the communication bridge.*
