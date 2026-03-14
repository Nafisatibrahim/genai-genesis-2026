from backend.schemas.intake import IntakePayload, RegionPain, PAIN_LEVEL_MIN, PAIN_LEVEL_MAX
from backend.schemas.outputs import AssessmentOutput, SafetyOutput, RecoveryOutput, ReferralOutput

# Valid intake
payload = IntakePayload(
    regions=[RegionPain(region_id="lower_back", level=4)],
    free_text="Hurt after sitting",
)
assert payload.regions[0].region_id == "lower_back" and payload.regions[0].level == 4

# Invalid: bad region_id or level out of range should raise
# IntakePayload(regions=[RegionPain(region_id="invalid", level=4)])  # -> ValidationError
# IntakePayload(regions=[RegionPain(region_id="lower_back", level=11)])  # -> ValidationError

# Valid outputs
AssessmentOutput(symptom_summary="Lower back pain.", risk_level="low", missing_info=[])
SafetyOutput(decision="safe_to_continue", triggered_red_flags=[])
RecoveryOutput(actions=["Stretch every hour"], precautions=[])
ReferralOutput(provider_type="none", reason="No referral needed")
print("Phase 1 schema tests passed!")