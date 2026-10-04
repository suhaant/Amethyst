-- PulsePatch care-team dashboard queries.
-- Paste each one into a dashboard dataset (see README.md). They assume the default
-- catalog and schema, workspace.pulsepatch; change the names if you set
-- DATABRICKS_CATALOG or DATABRICKS_SCHEMA.
-- "Latest assessment per wound" is the row with the newest generated_at for each wound.

-- 1. Wounds needing attention (counter)
WITH latest AS (
  SELECT *
  FROM workspace.pulsepatch.assessments
  QUALIFY ROW_NUMBER() OVER (PARTITION BY wound_id ORDER BY generated_at DESC) = 1
)
SELECT COUNT(*) AS wounds_needing_attention
FROM latest
WHERE tier IN ('2 treat', '3 intensive') OR COALESCE(recommend_clinician_review, FALSE);

-- 2. All wounds (table, highest risk first)
SELECT
  wound_id,
  ROUND(risk_score, 1)            AS risk_score,
  tier,
  confidence,
  recommend_clinician_review      AS needs_review,
  summary                         AS agent_summary,
  data_quality_flags,
  CASE
    WHEN skipped_reason IS NOT NULL THEN CONCAT('skipped: ', skipped_reason)
    WHEN us_40khz_min = 0 AND led_405nm_min = 0 THEN CONCAT('healing ultrasound ', us_1p5mhz_min, ' min')
    ELSE CONCAT('ultrasound ', us_40khz_min, ' min, light ', led_405nm_min, ' min (', led_dose_j_cm2, ' J/cm2)')
  END                             AS next_dose,
  assessed_by,
  generated_at                    AS assessed_at
FROM workspace.pulsepatch.assessments
QUALIFY ROW_NUMBER() OVER (PARTITION BY wound_id ORDER BY generated_at DESC) = 1
ORDER BY risk_score DESC;

-- 3. Sensor trends (line charts of ph, temp_c and impedance_kohm over time; filter on wound_id)
SELECT wound_id, `timestamp`, hour, ph, temp_c, impedance_kohm, source
FROM workspace.pulsepatch.readings
ORDER BY wound_id, `timestamp`;

-- 4. Risk history (line chart of risk_score over generated_at, one line per wound)
SELECT wound_id, generated_at, risk_score, tier, assessed_by
FROM workspace.pulsepatch.assessments
ORDER BY generated_at;
