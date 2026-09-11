-- RC3 activation bottleneck case: milestone and time-to-event views.
SELECT milestone, eligible_n, activated_n, activation_rate
FROM analytics.mart_activation_milestones
ORDER BY milestone_days;

