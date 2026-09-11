-- RC2 acquisition quality case: volume, conversion, downstream activation and value.
SELECT origin, mqls, converted_leads, conversion_rate
FROM analytics.mart_acquisition_conversion_by_origin
ORDER BY conversion_rate DESC;

