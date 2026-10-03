-- Dashboard queries (Databricks SQL). Replace workspace.wolfhacks with your catalog.schema.

-- 1. Risk over time per wound (line chart: x = timestamp, y = risk_score, series = wound_id)
SELECT wound_id, timestamp, risk_score, tier_name
FROM workspace.wolfhacks.risk_scores_gold
ORDER BY wound_id, timestamp;

-- 2. Current status of every wound (table, sorted by risk)
SELECT wound_id, risk_score, tier, led_dose_j_cm2, led_405nm_min, us_40khz_min, us_1p5mhz_min, `order`
FROM workspace.wolfhacks.treatment_plan_gold
ORDER BY risk_score DESC;

-- 3. Wounds needing attention (counter)
SELECT count(*) AS wounds_in_treat_or_intensive
FROM workspace.wolfhacks.treatment_plan_gold
WHERE tier IN ('2 treat', '3 intensive');

-- 4. Live demo (line chart, refresh while 05_live_demo runs)
SELECT timestamp, risk_score, p_infected, tier_name
FROM workspace.wolfhacks.live_risk_gold
ORDER BY timestamp;

-- 5. Model check on the demo set: predicted vs true label (bar chart)
SELECT a.label AS true_label, r.predicted_label, count(*) AS readings
FROM workspace.wolfhacks.risk_scores_gold r
JOIN workspace.wolfhacks.demo_answer_key a
  ON r.wound_id = a.wound_id AND r.timestamp = CAST(a.timestamp AS STRING)
GROUP BY 1, 2
ORDER BY 1, 2;
