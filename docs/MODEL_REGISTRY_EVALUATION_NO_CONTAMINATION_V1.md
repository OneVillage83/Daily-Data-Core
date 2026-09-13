# TDL Model Registry, Evaluation, and No-Contamination Protocol V1

Status: **governing scientific evaluation protocol**

Date locked: 2026-09-12

## 1. Purpose

The Daily Line will preserve every legitimate model experiment, its exact predictions, the information available at prediction time, and its forward evaluation. The system must be able to discover that a globally mediocre model is uniquely strong in one narrow regime without letting hindsight, market leakage, or duplicated models inflate the Unified Ensemble.

## 2. Model registry schema

Every registered model should be identifiable with fields equivalent to:

```text
model_id
model_family
algorithm
sport
target
role
status
market_dependency
training_window
feature_set_version
training_version
code_version
hyperparameter_version
created_at
retired_at
```

Recommended enumerations:

### Role
- `GENERALIST`
- `SPECIALIST`
- `COMPONENT_EXPERT`
- `RATING_SYSTEM`
- `SIMULATOR`
- `REGIME_DETECTOR`
- `FEATURE_MODEL`
- `CALIBRATOR`
- `META_MODEL`

### Status
- `RESEARCH`
- `SHADOW`
- `CHALLENGER`
- `CHAMPION`
- `SPECIALIST`
- `RETIRED`

### Market dependency
- `NONE` — eligible for the independent TDL path
- `HISTORICAL_MARKET_RESEARCH` — uses market data only in an explicitly separated research/evaluation role
- `CURRENT_MARKET_AWARE` — consumes PIT-eligible market state and is not eligible for the independent TDL Unified Line
- `EVALUATION_ONLY` — consumes result/closing evidence and can never be used for pregame inference

## 3. Prediction ledger schema

Every model run must append, not overwrite, a prediction record equivalent to:

```text
prediction_id
event_id
sport
target
model_id
model_version
prediction_timestamp
data_cutoff_timestamp
feature_snapshot_id
training_version

p_home_win
p_away_win
fair_moneyline_home
fair_moneyline_away
fair_spread
fair_total
expected_home_score
expected_away_score
uncertainty
confidence

input_quality_flags
missingness_flags
regime_labels
```

Where applicable, add complete distributional outputs and market-target probabilities.

## 4. Three required information clocks

Every evidence-backed input should preserve at least:

- `effective_at` — when the real-world state became true, if known;
- `published_at` — when the source says the information was published, if known;
- `observed_at` / `ingested_at` — when TDL acquired it;
- `available_at` — earliest defensible point at which a model may use it.

The canonical PIT eligibility test is:

```text
available_at <= prediction_cutoff
```

No later correction may silently move information backward in time.

## 5. The as-of rule

A historical backtest at timestamp `T` must behave as though `T` is literally the present.

The pipeline must not see:

- later injury reports;
- later starting lineups;
- later depth-chart changes;
- later weather forecasts or actual weather observations;
- later odds or prediction-market prices;
- closing lines;
- post-start information;
- final statistics;
- outcomes;
- corrected data whose correction was unavailable at `T`.

## 6. Training split constitution

Random shuffled cross-validation is not the primary validation framework for sports forecasting because it can mix future sports states into past prediction contexts.

Primary evaluation uses chronological / walk-forward splits.

Illustrative pattern:

```text
Train through 2022 -> predict 2023
Train through 2023 -> predict 2024
Train through 2024 -> predict 2025
```

Sports with different season structures may use equivalent rolling or expanding windows, but the future must remain future.

## 7. Stacker training must use out-of-fold / forward base predictions

A meta-ensemble may not train on a base model's in-sample predictions.

Forbidden:

```text
Train XGBoost on 2020-2025
Predict those same 2020-2025 games
Train stacker on those predictions
```

Required pattern:

```text
Base models train on past
        |
        v
Base models predict untouched future window
        |
        v
Predictions are frozen
        |
        v
Those frozen predictions become stacker training rows
```

The stacker learns only from predictions that the base models made without knowing the corresponding outcomes.

## 8. Calibration isolation

Calibration requires its own out-of-sample evidence. The preferred conceptual sequence is:

```text
BASE MODEL TRAINING
        |
        v
FORWARD / OOF PREDICTIONS
        |
        v
META-ENSEMBLE TRAINING
        |
        v
META-ENSEMBLE VALIDATION
        |
        v
CALIBRATION FIT
        |
        v
UNTOUCHED FINAL TEST
```

Exact folds may vary by sport and sample size, but the same games cannot casually serve as training, weight-selection, calibration, and final proof.

## 9. Test-set discipline

The final test window is sacred. Once developers inspect it and make design decisions in response, it is no longer a pristine test set; it becomes historical research evidence and the next forward window becomes the new test.

A poor final result is not permission to tune on that same result until it improves.

## 10. Learned Ensemble Importance

The Unified Ensemble measures multiple aspects of model value.

### Global skill
Long-run proper-scoring and target performance.

### Contextual skill
Performance conditioned on validated game/market regimes.

### Diversity value
Incremental information not already supplied by correlated models.

### Recent reliability
Forward evidence of drift/recovery, governed by minimum sample and shrinkage rules.

### Uncertainty
Model-reported and empirically estimated uncertainty.

### Sample support
The amount and representativeness of evidence behind a claimed specialty.

### Data quality
Freshness, completeness, input validity, and whether the model is operating inside its validated domain.

## 11. Specialist discovery

A model may be poor overall but valuable in a narrow regime. Specialist discovery should use forward predictions and minimum-support controls.

Example candidate expertise dimensions:

- wind / precipitation / temperature;
- indoor/outdoor venue;
- travel/rest differential;
- favorite/underdog band;
- early/mid/late season;
- injury/lineup uncertainty;
- rookie/backup QB;
- elite starter / bullpen stress in MLB;
- pace/rotation instability in basketball;
- goalie confirmation in NHL;
- surface in tennis;
- low/high expected-scoring regime;
- team-style or matchup clusters discovered by unsupervised models.

A specialist claim must survive forward validation. Post-hoc slicing without correction/support is not enough.

## 12. Specialist Contribution Score

The implementation may define a composite Specialist Contribution Score, but it should be based on concepts such as:

```text
specialist_value =
    contextual_proper_scoring_gain
    + ensemble_ablation_gain_in_regime
    + diversity_gain
    - uncertainty_penalty
    - small_sample_penalty
```

The exact numeric formula is a research object, not hard-coded by this document.

## 13. Diversity and duplication control

Two strong models that make nearly identical predictions do not provide twice the evidence.

Track at minimum:

- prediction correlation;
- residual correlation;
- disagreement frequency;
- incremental log-loss/Brier gain when added;
- ablation loss when removed;
- target/regime-specific overlap.

A simple diagnostic:

```text
D_ij = 1 - corr(P_i, P_j)
```

is useful but not sufficient by itself.

## 14. Weight is not importance

Maintain distinct measures:

- learned ensemble weight;
- permutation importance;
- ablation value;
- Shapley-style marginal contribution where feasible;
- unique residual skill;
- specialist/context value;
- diversity contribution.

A model with low average weight may still be critical in rare high-value regimes.

## 15. Model disagreement

Preserve the complete vector of model predictions. Do not store only the final average.

Useful diagnostics include:

```text
mean_probability
median_probability
std_probability
range_probability
max_pairwise_disagreement
weighted_disagreement
outlier_model_ids
```

High disagreement should usually widen uncertainty unless forward evidence establishes a reliable specialist pattern.

## 16. Dynamic weighting levels

The production system should conceptually separate:

### Level 1 — baseline weight
Long-run model value.

### Level 2 — context adjustment
Game/target/regime-specific expertise.

### Level 3 — confidence/data-quality adjustment
Whether today's inputs are fresh, complete, and inside the validated domain.

The effective model weight may therefore change from event to event and target to target.

## 17. Target-specific weights

A model does not receive one universal importance number.

Weights should support indexing by at least:

```text
model
sport
target
context/regime
prediction_horizon
```

For example, an NFL weather model may have low moneyline weight but high total weight.

## 18. Primary metrics

### Probability quality
- log loss
- Brier score
- calibration curve
- calibration intercept/slope
- ECE where useful
- Brier Skill Score relative to defined baseline

### Continuous targets
- spread MAE/RMSE where appropriate
- total MAE/RMSE
- score/distribution metrics

### Betting/decision evaluation
- price CLV
- line CLV
- ROI at actual available price
- ROI at sharp executable price
- edge-bucket performance
- opportunity count / bet count
- maximum drawdown
- expected-vs-realized value

### Scientific diagnostics
- ablation delta
- model diversity
- calibration by probability bucket
- performance by prediction horizon
- performance by regime
- performance by data-quality state

## 19. Required slicing

At minimum, reporting should be sliceable by:

```text
sport
market
target
season
prediction horizon
edge bucket
favorite/underdog
home/away
odds range
model agreement/disagreement
lineup/injury certainty
weather regime
model version
```

Sport repositories add sport-native slices.

## 20. Champion / Challenger promotion

A challenger may be promoted only after:

1. valid PIT inputs;
2. frozen forward predictions;
3. minimum sample/support criteria;
4. proper-scoring improvement or validated specialist contribution;
5. acceptable calibration;
6. no hidden market contamination for independent models;
7. ablation showing genuine ensemble value where relevant;
8. operational reproducibility;
9. no regression in protected targets/regimes without explicit accepted tradeoff.

## 21. Retention policy

Models are not deleted merely because they lose champion status. Preserve:

- code/version identifiers;
- training metadata;
- prediction history;
- evaluation history;
- known strengths and weaknesses;
- retirement reason;
- whether future re-evaluation is allowed.

This preserves the possibility that later evidence reveals a useful niche specialty.

## 22. Closing-line firewall

Closing-line evidence is evaluation-only for any earlier prediction timestamp.

Any feature pipeline that makes a historical close visible to a pre-close independent model invalidates that backtest window.

The system should test this invariant automatically.

## 23. Market contamination tests

Recommended automated assertions include:

- independent feature snapshots contain no market-price feature IDs;
- independent model manifests declare `market_dependency = NONE`;
- all input evidence satisfies PIT eligibility;
- no closing snapshot has `available_at <= prediction_cutoff` unless it genuinely existed at that time;
- stacker rows reference only frozen OOF/forward base predictions;
- calibrator rows do not overlap forbidden final-test rows;
- evaluation joins cannot mutate original prediction payloads.

## 24. Reproducibility packet

Every promoted model/version should be reproducible from a versioned packet containing or referencing:

- code commit;
- feature contract version;
- training-data manifest;
- point-in-time cutoff rules;
- hyperparameters;
- random seeds where relevant;
- model artifact checksum;
- calibration artifact checksum;
- stacker artifact checksum where applicable;
- evaluation window definition;
- metrics and slice reports.

## 25. Governing invariant

> **A model earns influence only through predictions it made without access to the answers, future information, or prohibited market information. The system preserves both successes and failures exactly as they occurred.**
