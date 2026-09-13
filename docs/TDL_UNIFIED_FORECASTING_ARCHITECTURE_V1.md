# The Daily Line Unified Forecasting Architecture V1

Status: **governing cross-sport modeling architecture**

Date locked: 2026-09-12

## 1. Purpose

The Daily Line (TDL) will not be built around one supposedly universal "best" sports-prediction algorithm. The production target is a **dynamic learned mixture-of-experts** that preserves many independent statistical, machine-learning, rating, simulation, and sport-native models; measures what each model is actually good at; learns when each model contributes unique information; combines only earned signal; and then calibrates the combined probability into the final **TDL Unified Line**.

The architecture must answer two different scientific questions without mixing them:

1. **Can The Daily Line independently predict the sporting outcome better than the market?**
2. **Can The Daily Line identify when the market is mispriced and when to act?**

Those are separate problems and must remain separate in code, data lineage, evaluation, and published terminology.

## 2. Locked terminology

### TDL Independent Model
A model whose prediction is produced without consuming sportsbook prices, exchange prices, prediction-market probabilities, future closing-line information, or features derived from those market values.

### TDL Independent Ensemble
The learned combination of eligible independent sport models before final probability calibration.

### TDL Unified Line
The **calibrated independent fair probability / fair line** produced by The Daily Line. This is the canonical proprietary TDL view.

The TDL Unified Line may be expressed as:

- fair win probability;
- fair moneyline;
- fair spread;
- fair total;
- score distribution;
- cover probability;
- over/under probability;
- market-specific fair price where supported.

### Market Consensus
The market-derived probability/line computed from eligible sportsbook, exchange, and/or prediction-market evidence. This is not the TDL Unified Line.

### TDL Market-Aware Decision Estimate
A separately labeled estimate used by the decision system after comparing the TDL Unified Line with market information. It may shrink or otherwise adjust confidence when historical evidence shows that certain disagreement patterns usually mean the independent TDL model is missing information. It must never overwrite or be relabeled as the TDL Unified Line.

### Line Timing Model (LTM)
A sport-specific model that estimates future market movement and expected execution value between the current time and game start. It answers **when to act**, not **who wins**.

## 3. Canonical production flow

```text
                         NON-MARKET DATA
                               |
        +----------------------+----------------------+
        |                      |                      |
 Historical data        Current sport state     Environment
        |                      |                      |
        |               injuries / lineups       weather / rest
        |               roster / player state    travel / venue
        |                      |                      |
        +----------------------+----------------------+
                               v
                     +--------------------+
                     |   TDL MODEL ZOO    |
                     +---------+----------+
                               |
      +------------------------+-------------------------+
      |                        |                         |
 Rating Models         Statistical Models          ML Models
 Elo / Glicko           Logistic / GLM / GAM        Random Forest
 SRS / Massey           Poisson / NegBin            XGBoost
 Bradley-Terry          mixed-effects               LightGBM
 custom power           Bayesian / state-space      CatBoost / SVM
      |                        |                         |
      +----------------+-------+-------------+-----------+
                       |                     |
                Sport Models          Simulation Models
                       |                     |
                MLB PA / pitcher         Monte Carlo
                NFL EPA / roster         drive / score
                NCAAF hierarchy          possession / event
                       |                     |
                       +----------+----------+
                                  v
                     INDEPENDENT META-ENSEMBLE
                                  |
                                  v
                         PROBABILITY CALIBRATOR
                                  |
                                  v
                    +---------------------------+
                    |      TDL UNIFIED LINE     |
                    |  Independent Fair View    |
                    +-------------+-------------+
                                  |
             +--------------------+--------------------+
             v                    v                    v
         Moneyline            Fair Spread          Fair Total
             |                    |                    |
             +--------------------+--------------------+
                                  |
                                  v
                       MARKET INTELLIGENCE LAYER
                                  ^
                                  |
              +-------------------+-------------------+
              |                   |                   |
            Opening            Current            Consensus
            market              market              market
              |                   |                   |
              +---- line history / velocity ----------+
              +---- prediction markets ---------------+
              +---- sharp / soft divergence ----------+
                                  |
                                  v
                         LINE TIMING MODEL
                                  |
                                  v
                    MARKET-RESIDUAL / EDGE MODEL
                                  |
                                  v
                           EXPECTED VALUE
                                  |
                                  v
                      UNCERTAINTY ADJUSTMENT
                                  |
                                  v
                           PLAY / PASS / AVOID
```

## 4. Non-negotiable separation of independent and market-aware paths

The independent sports path and the market-intelligence path are separate logical namespaces.

### Independent path MAY use

- historical game/player/team data;
- sport-native state and features;
- injuries and availability known by the prediction cutoff;
- confirmed or projected lineups known by the cutoff;
- weather forecasts available by the cutoff;
- venue, surface, travel, rest, recovery, coaching, and scheme state;
- non-market historical context that would have been available at the prediction time;
- sport-specific simulations;
- outputs of other independent models that satisfy the same cutoff.

### Independent path MUST NOT use

- sportsbook opening/current/closing prices as predictive features;
- consensus implied probability;
- prediction-market prices or probabilities;
- future line movement;
- closing lines for pregame inference;
- postgame information;
- any feature whose construction leaks one of the prohibited values.

Historical markets may be used in a **separate research/evaluation context** and in the market-aware decision path. They may not silently enter the model that is labeled TDL independent.

## 5. Model Zoo / Model Registry

TDL keeps a persistent catalog of legitimate models even when they are not currently part of the production ensemble. A model that is mediocre overall may still be the best known specialist for one regime, one target, or one component of a sport.

### 5.1 Statistical model families to track

- Linear Regression
- Multiple Linear Regression
- Ridge
- Lasso
- Elastic Net
- Logistic Regression
- Multinomial Logistic Regression
- Ordinal Regression
- Probit
- Generalized Linear Models (GLM)
- Generalized Additive Models (GAM)
- Poisson Regression
- Negative Binomial Regression
- Zero-inflated count models
- Mixed-effects models
- Hierarchical models
- ARIMA / SARIMA / ARIMAX
- Exponential Smoothing
- state-space models
- Kalman Filters
- Hidden Markov Models
- survival / hazard models

### 5.2 Bayesian families to track

- Bayesian Logistic Regression
- Bayesian GLMs
- Bayesian hierarchical models
- Bayesian dynamic models
- Bayesian state-space models
- Bayesian player-skill models
- Bayesian updating systems
- Bayesian networks where justified

### 5.3 Rating systems to track

- Elo
- Glicko / Glicko-2
- TrueSkill
- Massey
- Colley
- SRS
- Pythagorean expectation
- Bradley-Terry
- Thurstone-Mosteller
- sport-specific TDL power ratings
- contextual variants such as QB-adjusted, pitcher-adjusted, surface-adjusted, recency-adjusted, home-adjusted, or player-adjusted ratings

### 5.4 Traditional supervised ML to track

- Decision Trees
- Random Forest
- Extra Trees
- AdaBoost
- Gradient Boosting
- XGBoost
- LightGBM
- CatBoost
- Support Vector Machines
- K-Nearest Neighbors
- Gaussian Processes
- discriminant-analysis variants where appropriate

### 5.5 Neural / deep-learning families to track

- Multilayer Perceptrons
- RNN
- LSTM
- GRU
- Temporal CNN
- Transformers
- Temporal Fusion Transformer
- TabNet or successor tabular architectures
- learned embeddings
- graph neural networks

These are research candidates, not automatically preferred over simpler models.

### 5.6 Unsupervised / representation / regime models to track

- K-Means
- DBSCAN
- Gaussian Mixture Models
- hierarchical clustering
- PCA
- UMAP
- autoencoders
- anomaly detection
- regime classifiers

These models do not need to emit game probabilities. They may create latent state, clusters, anomaly flags, reduced feature spaces, or regime labels consumed by predictive models.

## 6. Model roles

Every registered model receives one or more explicit roles:

- `GENERALIST`
- `SPECIALIST`
- `COMPONENT_EXPERT`
- `RATING_SYSTEM`
- `SIMULATOR`
- `REGIME_DETECTOR`
- `FEATURE_MODEL`
- `CALIBRATOR`
- `META_MODEL`

A specialist is evaluated on whether it improves the ensemble in the regime for which it exists, not merely on whole-sport aggregate accuracy.

## 7. Outcome experts vs component experts

### Outcome experts
Directly predict targets such as:

- win probability;
- fair spread;
- fair total;
- expected score;
- cover probability;
- over/under probability;
- distributional outputs.

### Component experts
Estimate latent or causal sport components such as:

- quarterback efficiency;
- pitcher skill;
- batter skill;
- bullpen state;
- goalie quality;
- pace;
- possession efficiency;
- weather impact;
- injury impact;
- offensive-line / defensive-front mismatch;
- player availability or minutes;
- coaching / scheme state.

Component experts feed sport-native models, simulations, or meta-models rather than being forced to vote directly on the game winner.

## 8. Standardized prediction contract

Every predictive model must emit a versioned contract containing, at minimum:

```text
event_id
sport
model_id
model_version
model_role
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
```

Where supported, add:

```text
distribution_home_score
distribution_away_score
p_cover_home
p_cover_away
p_over
p_under
```

The contract must allow the meta-ensemble to consume Elo, XGBoost, Bayesian, simulation, and future model families without special-case glue for each algorithm.

## 9. Dynamic Learned Ensemble Importance

TDL does not simply average models and does not assign one permanent weight per model.

For model `i`, target `t`, and context `c`, the effective contribution is conceptually:

```text
w(i,t,c) = f(
    global_skill,
    contextual_skill,
    diversity_value,
    recent_reliability,
    uncertainty,
    sample_support,
    data_quality,
    target_specific_skill
)
```

### 9.1 Global skill
Long-run probability quality and target performance.

### 9.2 Contextual skill
How well the model performs in the current regime. Examples:

- high-wind NFL games;
- rookie-QB starts;
- early-season NCAAF;
- MLB games with elite starting pitching;
- NBA/WNBA rotation instability;
- soccer low-event regimes;
- tennis surface-specific matchups.

### 9.3 Diversity / unique signal
Models that are nearly duplicates should not receive duplicate credit. Prediction correlation and incremental out-of-fold value are measured explicitly.

One simple diagnostic is:

```text
D_ij = 1 - corr(P_i, P_j)
```

This is a diagnostic, not the sole production weighting formula.

### 9.4 Recent reliability
A model may be down-weighted when documented drift or regime change appears, but recent performance never permits future leakage or ad-hoc post-result tuning.

### 9.5 Uncertainty and data quality
A normally strong model can receive reduced effective weight when its required inputs are missing, stale, low-confidence, or outside its validated domain.

### 9.6 Target-specific weighting
There is no universal model weight. A model may deserve one weight for moneyline, another for spread, and another for total.

## 10. Specialist Contribution Score / expertise map

The registry should preserve a per-model expertise map such as:

```text
MODEL: NFL-WEATHER-GBM-v3

Overall skill:
    Brier: ...
    log loss: ...

Strong regimes:
    wind > threshold
    low temperature
    outdoor venues

Weak regimes:
    dome games
    neutral weather

Strong targets:
    total
    team scoring

Weak targets:
    moneyline

Unique residual contribution:
    ...

Prediction correlation:
    vs model A: ...
    vs model B: ...
```

A model may have low global rank and still remain in production as a validated specialist.

## 11. Weight is not the same as importance

The system records multiple notions of model value:

- learned ensemble weight;
- permutation importance;
- ablation value (performance loss when removed);
- Shapley-style marginal contribution where computationally practical;
- unique residual skill;
- diversity contribution;
- context-specific performance.

A model with a small numerical weight can still be important if removing it materially worsens calibration or performance in an important regime.

## 12. Model disagreement is a signal

TDL preserves disagreement rather than averaging it away.

For model probabilities `p_1...p_n`, ensemble dispersion/variance is tracked as an uncertainty feature. A large outlier can indicate:

1. a real specialist signal;
2. model failure;
3. bad/stale input data;
4. a rare regime;
5. an event that needs human/model audit.

Historical out-of-fold evidence determines whether a particular outlier pattern should increase or decrease final confidence.

## 13. Calibration

The raw ensemble is not automatically The Daily Line. A separate calibration layer transforms the Unified Raw Forecast into the **TDL Unified Line**.

Candidate calibrators may include:

- Platt/logistic calibration;
- isotonic regression;
- beta calibration;
- sport/target-specific calibrated Bayesian mapping;
- other methods that prove superior on untouched chronological data.

Calibration is evaluated with proper scoring rules and calibration diagnostics rather than winner accuracy alone.

## 14. Core evaluation hierarchy

Primary metrics:

- log loss;
- Brier score;
- calibration curve;
- calibration intercept/slope;
- Brier Skill Score versus relevant baseline/market where defined.

Secondary/target metrics:

- accuracy;
- spread MAE;
- total MAE;
- score MAE/distribution metrics;
- ECE or other calibration-error summaries.

Betting / decision metrics:

- closing-line value (price and line CLV);
- ROI at actually available price;
- ROI against sharp-book executable prices;
- edge-bucket performance;
- bet count / opportunity count;
- maximum drawdown;
- model disagreement at decision time;
- timing-to-start performance.

## 15. Champion / Challenger governance

The registry preserves all legitimate research models with statuses such as:

- `RESEARCH`
- `SHADOW`
- `CHALLENGER`
- `CHAMPION`
- `SPECIALIST`
- `RETIRED`

A challenger replaces or joins a champion only after earning promotion on chronological, point-in-time-correct, untouched forward evidence. Backtest attractiveness alone is insufficient.

No model is deleted merely because it is not currently a champion. Historical predictions, versions, strengths, weaknesses, and evaluation remain preserved.

## 16. Immutable prediction ledger

Predictions are append-only scientific observations. Never overwrite an earlier prediction when a model reruns.

If a model predicts 63.1% at noon and 61.8% at 17:00 after new information, both records remain.

Required lineage includes:

- prediction timestamp;
- event/game identity;
- model/version;
- data cutoff;
- feature snapshot;
- training version;
- output contract;
- uncertainty;
- later-linked result and closing-market evaluation.

This supports questions such as:

- Did later information improve forecast quality?
- Does the noon forecast beat the pregame forecast?
- When does a sport's prediction quality peak?
- Which model first identified a useful edge?
- Which model systematically overreacts to late information?

## 17. Final TDL vs market example

```text
Market no-vig probability      56.2%

TDL MODELS
Elo / Power Rating             61.8%
Logistic / GLM                 60.7%
XGBoost                        63.1%
LightGBM                       62.8%
Bayesian                       61.2%
Simulation                     62.4%
Player model                   64.0%
Weather-aware specialist       63.2%

TDL Independent Ensemble       62.5%
TDL Unified Line               61.9%

Market                         56.2%
Independent TDL edge           +5.7 percentage points
```

The market value is never used to make the independent 61.9% number. It is compared only after the TDL Unified Line exists.

## 18. Market-aware decision layer

After the TDL Unified Line exists, a separate decision layer may combine:

- opening market;
- current market;
- no-vig consensus;
- sharp-book consensus;
- soft-book dispersion;
- line movement, velocity, and acceleration;
- prediction-market prices;
- liquidity/volume where available;
- TDL independent edge;
- model disagreement;
- uncertainty;
- Line Timing Model output;
- historical residual behavior.

This layer may produce:

- market-aware decision probability;
- expected value;
- usable edge after uncertainty;
- `PLAY`, `LEAN`, `PASS`, or `AVOID`;
- `BET_NOW`, `WAIT`, or equivalent timing instruction.

It may never retroactively alter the stored independent TDL Unified Line.

## 19. Market residual model

A separate residual learner may estimate where the market tends to be wrong. Conceptually:

```text
residual = outcome - p_market
predicted_residual = f(non_leaking_context, independent_model_outputs, market_state)
p_market_aware = constrain(p_market + predicted_residual)
```

This is a market-aware decision model, not an independent sports model. Its output must be labeled accordingly.

## 20. Uncertainty-adjusted usable edge

The Recommendation Gate should not act on raw difference alone. A conceptual form is:

```text
usable_edge =
    raw_edge
    - model_uncertainty_penalty
    - calibration_uncertainty_penalty
    - market/execution_uncertainty_penalty
```

The exact production function is learned/validated by sport and market; the architectural requirement is that uncertainty is explicit rather than hidden.

## 21. Sport-specific starting architectures

The shared framework does not force identical model families on each sport.

### MLB
Prioritize hierarchical player-skill models, pitcher/batter interactions, bullpen and lineup state, park/environment models, PA/run generative simulation, plus tree-based and rating challengers.

### NFL
Prioritize EPA/success-rate, player/QB and roster state, power ratings, matchup models, drive/game simulation, tree-based challengers, and contextual specialists.

### NCAAF
Prioritize diverse team-strength/rating systems, hierarchical priors, roster/coach/team state, football simulation, and explicit opening-line/timing evaluation.

### NBA / WNBA
Prioritize player/team efficiency, minutes/rotation state, possession models, tree-based and Bayesian models, simulation, and calibrated probability quality.

### NHL
Prioritize xG/shot-quality, goalie state, special teams, rest/fatigue, scoring distributions, and Monte Carlo simulation.

### Soccer
Prioritize xG, score-distribution models such as Poisson/Skellam families, calibration, team-strength models, and market-residual challengers.

### Tennis
Prioritize surface-aware rating systems, serve/return and player-form features, Elo/ML hybrids, calibration, and matchup-specific specialists.

### Golf
Prioritize strokes-gained latent ability, course fit, field strength, weather, and tournament simulation.

## 22. Architectural invariant

The final principle is:

> **Every model contributes only the portion of the sports-prediction problem that it has demonstrated, on point-in-time-correct forward evidence, that it understands better or differently than the rest of the system.**

The calibrated synthesis of that validated independent knowledge is the **TDL Unified Line**.
