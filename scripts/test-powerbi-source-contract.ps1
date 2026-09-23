param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

$modelRoot = Join-Path $ProjectRoot 'deliverables\powerbi\final market dashboard.SemanticModel\definition'
$tableRoot = Join-Path $modelRoot 'tables'
$dataRoot = Join-Path $ProjectRoot 'deliverables\powerbi\source-data\release_v3_final'

if (-not (Test-Path (Join-Path $modelRoot 'expressions.tmdl'))) {
    throw 'Missing DataRoot expression.'
}

$requiredFiles = @(
    'reports\headline_metrics.json',
    'reports\qa\period_completeness.csv',
    'reports\statistics\concentration_statistics.csv',
    'reports\tables\mart_acquisition_channel.csv',
    'reports\tables\mart_category_performance.csv',
    'reports\tables\mart_geography_performance.csv',
    'reports\tables\mart_marketplace_monthly.csv',
    'reports\tables\mart_seller_lifetime.csv',
    'reports\tables\powerbi_activation_cohort.csv',
    'reports\tables\powerbi_commercial_segment.csv',
    'reports\tables\powerbi_customer_experience.csv',
    'reports\tables\powerbi_decision_register.csv',
    'reports\tables\powerbi_decision_matrix_plot.csv',
    'reports\tables\powerbi_highlights.csv',
    'reports\tables\powerbi_insights.csv',
    'reports\tables\powerbi_retention_cohort.csv',
    'reports\tables\powerbi_root_cause_register.csv'
)

$missingFiles = $requiredFiles | Where-Object { -not (Test-Path (Join-Path $dataRoot $_)) }
if ($missingFiles) {
    throw ('Missing governed input files: ' + ($missingFiles -join ', '))
}

$csvTableContracts = @{
    AcquisitionChannel = 'mart_acquisition_channel.csv'
    ActivationCohort = 'powerbi_activation_cohort.csv'
    CommercialSegment = 'powerbi_commercial_segment.csv'
    CustomerExperience = 'powerbi_customer_experience.csv'
    DecisionRegister = 'powerbi_decision_register.csv'
    DecisionMatrix = 'powerbi_decision_matrix_plot.csv'
    Geo = 'mart_geography_performance.csv'
    Highlights = 'powerbi_highlights.csv'
    Insights = 'powerbi_insights.csv'
    RetentionCohort = 'powerbi_retention_cohort.csv'
    RootCauseRegister = 'powerbi_root_cause_register.csv'
}

$exceptionTables = Get-ChildItem -LiteralPath $tableRoot -Filter '*.tmdl' |
    Where-Object { (Get-Content -LiteralPath $_.FullName -Raw) -match 'PBI_ResultType\s*=\s*Exception' }
if ($exceptionTables) {
    throw ('Power Query result metadata still marks an exception: ' + ($exceptionTables.Name -join ', '))
}

foreach ($tableName in $csvTableContracts.Keys) {
    $file = Join-Path $dataRoot ('reports\tables\' + $csvTableContracts[$tableName])
    $headers = (Import-Csv -LiteralPath $file | Select-Object -First 1).PSObject.Properties.Name
    $definition = Join-Path $tableRoot ($tableName + '.tmdl')
    $definitionText = Get-Content -LiteralPath $definition -Raw
    if ($definitionText -notmatch 'PBI_ResultType\s*=\s*Table') {
        throw "$tableName is an import table but lacks PBI_ResultType = Table metadata."
    }
    $requiredColumns = Select-String -LiteralPath $definition -Pattern '^\s*sourceColumn:\s*(.+)$' |
        ForEach-Object { $_.Matches[0].Groups[1].Value.Trim('"') }
    # Power Query may rename a governed source field before the model column
    # is bound. Keep the contract check aware of those explicit mappings.
    $sourceAliases = @{}
    $partition = $definitionText
    [regex]::Matches($partition, '\{\{"([^\"]+)",\s*"([^\"]+)"\}\}') | ForEach-Object {
        $sourceAliases[$_.Groups[2].Value] = $_.Groups[1].Value
    }
    $missingColumns = $requiredColumns | Where-Object {
        $alias = if ($sourceAliases.ContainsKey($_)) { $sourceAliases[$_] } else { $_ }
        ($_ -notin $headers) -and ($alias -notin $headers)
    }
    if ($missingColumns) {
        throw "$tableName has fields absent from $($csvTableContracts[$tableName]): $($missingColumns -join ', ')"
    }
}

$legacyReferences = rg -n -i 'bi_fact_marketplace_item|Demo[A-Z]|Partner converts|PROTOTYPE.*MOCK' $modelRoot (Join-Path $ProjectRoot 'deliverables\powerbi\final market dashboard.Report\definition')
if ($LASTEXITCODE -eq 0 -and $legacyReferences) {
    throw ('Legacy or unsupported report references found:' + [Environment]::NewLine + ($legacyReferences -join [Environment]::NewLine))
}
if ($LASTEXITCODE -gt 1) { throw 'Unable to scan Power BI definitions.' }

$activationRows = @(Import-Csv -LiteralPath (Join-Path $dataRoot 'reports\tables\powerbi_activation_cohort.csv'))
foreach ($row in $activationRows) {
    foreach ($horizon in @('30', '60', '90')) {
        $observable = [int]$row.("Observable${horizon}D")
        $activated = [int]$row.("Activated${horizon}D")
        $displayText = [string]$row.("Activated${horizon}DDisplay")
        $rateText = [string]$row.("Activation${horizon}Rate")
        if ($observable -eq 0 -and $rateText.Trim() -ne '') {
            throw "Activation${horizon}Rate must be blank when Observable${horizon}D is zero for $($row.Cohort)."
        }
        if ($observable -eq 0 -and $displayText.Trim() -ne '') {
            throw "Activated${horizon}DDisplay must be blank when Observable${horizon}D is zero for $($row.Cohort)."
        }
        if ($observable -gt 0 -and $activated -gt $observable) {
            throw "Activated${horizon}D exceeds Observable${horizon}D for $($row.Cohort)."
        }
        if ($observable -gt 0 -and [int]$displayText -ne $activated) {
            throw "Activated${horizon}DDisplay does not match the observed numerator for $($row.Cohort)."
        }
    }
}

$rootHeaders = (Import-Csv -LiteralPath (Join-Path $dataRoot 'reports\tables\powerbi_root_cause_register.csv') | Select-Object -First 1).PSObject.Properties.Name
$forbiddenRootFields = @('Impact', 'Severity', 'Frequency', 'PriorityScore')
$invalidRootFields = $forbiddenRootFields | Where-Object { $_ -in $rootHeaders }
if ($invalidRootFields) {
    throw ('Root-cause source still exposes synthetic scoring fields: ' + ($invalidRootFields -join ', '))
}
$rc5 = Import-Csv -LiteralPath (Join-Path $dataRoot 'reports\tables\powerbi_root_cause_register.csv') |
    Where-Object { $_.Case -eq 'RC5' } | Select-Object -First 1
if (-not $rc5 -or $rc5.EvidenceStatus -ne 'Supported operational association') {
    throw 'RC5 must use the governed operational-association wording.'
}

$decisions = @(Import-Csv -LiteralPath (Join-Path $dataRoot 'reports\tables\powerbi_decision_register.csv'))
$d04 = $decisions | Where-Object { $_.Action -match 'top 1/5/10/20%' } | Select-Object -First 1
if (-not $d04 -or $d04.Priority -ne 'P2' -or $d04.TimeHorizon -ne 'monthly') {
    throw 'Decision register D04 priority/cadence contract failed.'
}

Write-Output 'Power BI source contract passed.'
