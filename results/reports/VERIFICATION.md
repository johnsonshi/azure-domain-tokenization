# Verification report

Profile: `pilot`  
_Deterministic report — regenerate with `uv run msdocs-tok verify --profile pilot` (or `make verify`)._

| Check | Result | Detail |
|---|---|---|
| byte_match_ok | PASS | {'azure': 33554432, 'general': 33554432, 'mixed': 33554432} |
| no_leakage | PASS | [] |
| leakage_controls_present | PASS | cross_corpus_removed=9 |
| roundtrip_all_ok | PASS | 0 failures |
| totals_reconcile | PASS |  |
| provenance_complete | PASS |  |
| artifact_distribution_marked | PASS | all_marked=True, no_tokenizer_json_committed=True |
| sources_lock_exists | PASS |  |

**Overall: ALL CHECKS PASS** (8/8)
