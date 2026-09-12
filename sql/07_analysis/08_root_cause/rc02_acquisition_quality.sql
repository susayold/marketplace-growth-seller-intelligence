-- RC2: compare origin quality with volume and downstream guardrails.
SELECT * FROM analytics.mart_acquisition_conversion_by_origin
ORDER BY conversion_rate DESC;