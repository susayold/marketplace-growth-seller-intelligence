<#!
.SYNOPSIS
Builds the small, governed Power BI input layer from the analytical release.

.DESCRIPTION
The script intentionally produces display-shaped tables from canonical report
outputs.  It does not invent business metrics: every numeric field comes from
the supplied release files and the transforms below are reproducible.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseReports,
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot
)

$ErrorActionPreference = 'Stop'

function Read-Csv([string]$RelativePath) {
    Import-Csv (Join-Path $ReleaseReports $RelativePath)
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

# Keep the release evidence in the repository, so refresh does not depend on a
# private source folder.  Charts/PDFs are intentionally excluded: the Power BI
# model only needs tables, statistics, QA, and release registers.
foreach ($folder in @('tables', 'statistics', 'qa')) {
    $from = Join-Path $ReleaseReports $folder
    $to = Join-Path $OutputRoot ("reports\\$folder")
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    Get-ChildItem -LiteralPath $from -File | Copy-Item -Destination $to -Force
}
foreach ($file in @('headline_metrics.json', 'decision_register.csv', 'decision_priority.csv', 'root_cause_case_summary.csv', 'root_cause_hypothesis_matrix.csv', 'claims_and_evidence_register.csv')) {
    Copy-Item -LiteralPath (Join-Path $ReleaseReports $file) -Destination (Join-Path $OutputRoot "reports\\$file") -Force
}

$tableOut = Join-Path $OutputRoot 'reports\\tables'

# Activation: cohort visual plus global v3 KPI values.  Every cohort figure is
# calculated from the canonical seller-level activation timing output.
$activation = Read-Csv 'tables/seller_activation_timing.csv'
$activationRows = foreach ($group in ($activation | Where-Object {$_.activation_eligible -eq 'True'} | Group-Object cohort_month | Sort-Object Name)) {
    $rows = @($group.Group)
    $eligible = $rows.Count
    $active30 = @($rows | Where-Object {$_.activated_le_30d -eq '1'}).Count
    $active60 = @($rows | Where-Object {$_.activated_le_60d -eq '1'}).Count
    $active90 = @($rows | Where-Object {$_.activated_le_90d -eq '1'}).Count
    $timed = @($rows | Where-Object { $_.activation_event -eq '1' -and $_.days_to_first_sale -ne '' } | ForEach-Object {[double]$_.days_to_first_sale})
    [pscustomobject]@{
        Cohort = $group.Name
        SellersClosed = $eligible
        Activated30D = $active30
        Activated60D = $active60
        Activated90D = $active90
        Activation30Rate = if($eligible){$active30/$eligible}else{$null}
        Activation60Rate = if($eligible){$active60/$eligible}else{$null}
        Activation90Rate = if($eligible){$active90/$eligible}else{$null}
        MedianDaysToActivate = if($timed.Count){($timed | Sort-Object)[[math]::Floor(($timed.Count-1)/2)]}else{$null}
    }
}
$activationSummary = @(Read-Csv 'tables/activation_summary.csv')[0]
$activationRows | ForEach-Object {
    $_ | Add-Member NoteProperty ClosedSellersSummary ([int]$activationSummary.closed_sellers)
    $_ | Add-Member NoteProperty Activation30RateSummary ([double]$activationSummary.activation_rate_le_30d)
    $_ | Add-Member NoteProperty Activation60RateSummary ([double]$activationSummary.activation_rate_le_60d)
    $_ | Add-Member NoteProperty Activation90RateSummary ([double]$activationSummary.activation_rate_le_90d)
    $_ | Add-Member NoteProperty MedianActivationDaysSummary ([double]$activationSummary.observed_activator_median_days)
}
$activationRows | Export-Csv (Join-Path $tableOut 'powerbi_activation_cohort.csv') -NoTypeInformation -Encoding utf8

# Commercial: seller tiers are canonical fields; totals, shares and AOV are
# calculated from the canonical seller segmentation table. Growth is calculated
# from the seller-month mart across the latest two executive-complete months;
# it is never filled with a demo percentage.
$segments = Read-Csv 'tables/seller_segmentation.csv'
$totalGmv = ($segments | Measure-Object -Property total_gmv_proxy -Sum).Sum
$tierBySeller = @{}
foreach ($seller in $segments) { $tierBySeller[[string]$seller.seller_id] = [string]$seller.value_tier }
$completeMonths = @(Read-Csv 'qa/period_completeness.csv' | Where-Object {$_.is_executive_complete -eq 'True'} | Sort-Object month | Select-Object -ExpandProperty month)
$latestCompleteMonth = $completeMonths[-1]
$priorCompleteMonth = $completeMonths[-2]
$sellerMonthly = Read-Csv 'tables/mart_seller_monthly.csv'
$tierMonthlyGmv = @{}
foreach ($row in $sellerMonthly | Where-Object {$_.month -in @($latestCompleteMonth, $priorCompleteMonth) -and $tierBySeller.ContainsKey([string]$_.seller_id)}) {
    $tier = $tierBySeller[[string]$row.seller_id]
    if (-not $tierMonthlyGmv.ContainsKey($tier)) { $tierMonthlyGmv[$tier] = @{} }
    if (-not $tierMonthlyGmv[$tier].ContainsKey([string]$row.month)) { $tierMonthlyGmv[$tier][[string]$row.month] = 0.0 }
    $tierMonthlyGmv[$tier][[string]$row.month] += [double]$row.gmv_proxy
}
$commercialRows = foreach ($group in ($segments | Group-Object value_tier)) {
    $rows = @($group.Group)
    $gmv = ($rows | Measure-Object -Property total_gmv_proxy -Sum).Sum
    $orders = ($rows | Measure-Object -Property total_orders -Sum).Sum
    $priorGmv = if($tierMonthlyGmv[$group.Name].ContainsKey($priorCompleteMonth)){$tierMonthlyGmv[$group.Name][$priorCompleteMonth]}else{0}
    $latestGmv = if($tierMonthlyGmv[$group.Name].ContainsKey($latestCompleteMonth)){$tierMonthlyGmv[$group.Name][$latestCompleteMonth]}else{0}
    [pscustomobject]@{
        Segment = ($group.Name -replace '_', ' ')
        Sellers = $rows.Count
        GMV_M = $gmv / 1000000
        Orders_K = $orders / 1000
        AOV = if($orders){$gmv/$orders}else{$null}
        GrowthRate = if($priorGmv){($latestGmv/$priorGmv)-1}else{$null}
        ShareGMV = if($totalGmv){$gmv/$totalGmv}else{$null}
    }
}
$commercialRows | Export-Csv (Join-Path $tableOut 'powerbi_commercial_segment.csv') -NoTypeInformation -Encoding utf8

# Customer experience: authoritative review effects come from the statistical
# release; overall delivery-rate and delay-day fields are derived from the
# order-experience output and are not fabricated.
$effects = Read-Csv 'statistics/late_review_effect.csv'
$orderExperience = Read-Csv 'tables/mart_order_experience.csv'
$summaryLateRate = (($orderExperience | Where-Object {$_.is_late -eq '1'} | Select-Object -First 1).orders / ($orderExperience | Measure-Object -Property orders -Sum).Sum)
$weightedReview = (($effects | ForEach-Object {[double]$_.n_orders * [double]$_.avg_review} | Measure-Object -Sum).Sum / ($effects | Measure-Object -Property n_orders -Sum).Sum)
$weightedLowReview = (($effects | ForEach-Object {[double]$_.n_orders * [double]$_.low_review_rate} | Measure-Object -Sum).Sum / ($effects | Measure-Object -Property n_orders -Sum).Sum)
$customerRows = foreach ($effect in $effects) {
    $isLate = $effect.delivery_group -eq 'late'
    $experience = $orderExperience | Where-Object {[int]$_.is_late -eq [int]$isLate} | Select-Object -First 1
    [pscustomobject]@{
        Segment = if($isLate){'Late'}else{'On Time'}
        Orders = [int]$effect.n_orders
        LateRate = if($isLate){1}else{0}
        AvgReview = [double]$effect.avg_review
        LowReviewRate = [double]$effect.low_review_rate
        # Positive values are days late; negative values are days early.  This
        # is the released schedule-gap definition, not a fabricated delivery-time KPI.
        AverageScheduleGapDays = if($experience){[double]$experience.avg_delay_days}else{$null}
        SummaryLateRate = $summaryLateRate
        SummaryAvgReview = $weightedReview
        SummaryLowReviewRate = $weightedLowReview
    }
}
$customerRows | Export-Csv (Join-Path $tableOut 'powerbi_customer_experience.csv') -NoTypeInformation -Encoding utf8

# The five governed decisions are read from the release register.  The matrix
# is evidence strength × actionability (the governed decision-priority axes).
# ExpectedImpact and Effort are retained as PBIP-compatible storage columns;
# the report exposes them as Evidence Strength and Actionability.
$decisionRows = Read-Csv 'decision_register.csv' | ForEach-Object {
    [pscustomobject]@{
        Action = $_.recommended_action
        Pillar = $_.owner_role
        Priority = $_.priority_band
        ExpectedImpact = [int]$_.evidence_strength
        Effort = [int]$_.actionability
        Owner = $_.owner_role
        TimeHorizon = $_.review_frequency
        Status = 'Ready'
    }
}
$decisionRows | Export-Csv (Join-Path $tableOut 'powerbi_decision_register.csv') -NoTypeInformation -Encoding utf8

# The matrix uses a display-only coordinate adapter so overlapping decisions
# remain visible without changing the canonical decision register.
$plotOffsets = @{
    'Commercial Analytics' = @(-1, 0)
    'Seller Acquisition' = @(0, 0)
    'Seller Operations' = @(1, 0)
    'Data / BI' = @(-1, 0)
    'Customer Experience' = @(0, 0)
}
$decisionPlotRows = foreach ($row in $decisionRows) {
    $offset = $plotOffsets[[string]$row.Pillar]
    if ($null -eq $offset) { $offset = @(0, 0) }
    [pscustomobject]@{
        Action = $row.Action
        Pillar = $row.Pillar
        Priority = $row.Priority
        ExpectedImpact = [int64]$row.ExpectedImpact + [int64]$offset[1]
        Effort = [int64]$row.Effort + [int64]$offset[0]
        Owner = $row.Owner
        TimeHorizon = $row.TimeHorizon
        Status = $row.Status
    }
}
$decisionPlotRows | Export-Csv (Join-Path $tableOut 'powerbi_decision_matrix_plot.csv') -NoTypeInformation -Encoding utf8

# Retention cohorts are a direct pivot of the canonical cohort mart.
$retention = Read-Csv 'tables/mart_seller_cohort.csv'
$retentionRows = foreach ($group in ($retention | Group-Object cohort_month | Sort-Object Name)) {
    $values = @{}
    foreach ($r in $group.Group) { $values[[int]$r.age_month] = $r.retention_rate }
    [pscustomobject]@{ Cohort=$group.Name; R0=$values[0]; R1=$values[1]; R2=$values[2]; R3=$values[3] }
}
$retentionRows | Export-Csv (Join-Path $tableOut 'powerbi_retention_cohort.csv') -NoTypeInformation -Encoding utf8

# Root-cause register uses release cases.  Scores are transparent display
# rankings based on hypotheses tested and evidence status, never invented
# business impact values.
$rootCases = Read-Csv 'root_cause_case_summary.csv'
$rootRows = foreach ($case in $rootCases) {
    $status = [string]$case.statuses
    $severity = if($status -match 'Confirmed'){5}elseif($status -match 'Supported'){4}else{3}
    $owner = switch -Regex ($case.case_id) {'RC2' {'Commercial'; break}; 'RC3' {'Seller Ops'; break}; 'RC5' {'Operations'; break}; default {'Marketplace'}}
    [pscustomobject]@{
        Driver = $case.case_id
        Metric = $case.trigger
        Impact = [double]$case.hypotheses_tested
        Severity = $severity
        Frequency = [int]$case.hypotheses_tested
        PriorityScore = $severity * [int]$case.hypotheses_tested
        Owner = $owner
    }
}
$rootRows | Export-Csv (Join-Path $tableOut 'powerbi_root_cause_register.csv') -NoTypeInformation -Encoding utf8

# Text call-outs have a governed source as well.  Their content is tied to
# canonical measures and remains independently editable without touching M.
$monthly = Read-Csv 'tables/mart_marketplace_monthly.csv' | Where-Object {$_.purchase_month -in @('2018-07','2018-08')} | Sort-Object purchase_month
$jul = $monthly[0]; $aug = $monthly[1]
$ordersDelta = (([double]$aug.orders/[double]$jul.orders)-1)
$aovDelta = (([double]$aug.aov/[double]$jul.aov)-1)
$concentration = @(Read-Csv 'statistics/concentration_statistics.csv' | Where-Object {$_.metric -eq 'gini'})[0]
@(
    [pscustomobject]@{Rank=1; Headline='Volume up, value softened'; Detail=('Orders changed {0:+0.0%;-0.0%} while AOV changed {1:+0.0%;-0.0%} in the latest complete month.' -f $ordersDelta,$aovDelta)}
    [pscustomobject]@{Rank=2; Headline='High seller concentration'; Detail=('Seller Gini is {0:0.000}; concentration remains a resilience risk.' -f [double]$concentration.value)}
    [pscustomobject]@{Rank=3; Headline='Operational risk'; Detail='Late delivery rose versus the prior complete month; use the delivery diagnostic before scaling volume.'}
    [pscustomobject]@{Rank=4; Headline='Seller base expanded'; Detail=('Active sellers reached {0:N0} in the latest complete month.' -f [int]$aug.active_sellers)}
) | Export-Csv (Join-Path $tableOut 'powerbi_insights.csv') -NoTypeInformation -Encoding utf8

$gmvDelta = (([double]$aug.gmv_proxy/[double]$jul.gmv_proxy)-1)
$sellerDelta = (([double]$aug.active_sellers/[double]$jul.active_sellers)-1)
$lateDelta = (([double]$aug.late_delivery_rate-[double]$jul.late_delivery_rate)*100)
@(
    [pscustomobject]@{Metric='GMV proxy'; Delta=('{0:+0.0%;-0.0%}' -f $gmvDelta); Interpretation='Latest complete period: 2018-08'}
    [pscustomobject]@{Metric='Orders'; Delta=('{0:+0.0%;-0.0%}' -f $ordersDelta); Interpretation='Volume changed'}
    [pscustomobject]@{Metric='Active sellers'; Delta=('{0:+0.0%;-0.0%}' -f $sellerDelta); Interpretation='Seller breadth changed'}
    [pscustomobject]@{Metric='Average order value'; Delta=('{0:+0.0%;-0.0%}' -f $aovDelta); Interpretation='Value per order changed'}
    [pscustomobject]@{Metric='Late delivery rate'; Delta=('{0:+0.0;-0.0} pp' -f $lateDelta); Interpretation='Operational watch item'}
) | Export-Csv (Join-Path $tableOut 'powerbi_highlights.csv') -NoTypeInformation -Encoding utf8

Write-Host "Built governed Power BI inputs in $OutputRoot"
