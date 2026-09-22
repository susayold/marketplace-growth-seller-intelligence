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
    Highlights = 'powerbi_highlights.csv'
    Insights = 'powerbi_insights.csv'
    RetentionCohort = 'powerbi_retention_cohort.csv'
    RootCauseRegister = 'powerbi_root_cause_register.csv'
}

foreach ($tableName in $csvTableContracts.Keys) {
    $file = Join-Path $dataRoot ('reports\tables\' + $csvTableContracts[$tableName])
    $headers = (Import-Csv -LiteralPath $file | Select-Object -First 1).PSObject.Properties.Name
    $definition = Join-Path $tableRoot ($tableName + '.tmdl')
    $requiredColumns = Select-String -LiteralPath $definition -Pattern '^\s*sourceColumn:\s*(.+)$' |
        ForEach-Object { $_.Matches[0].Groups[1].Value.Trim('"') }
    # Power Query may rename a governed source field before the model column
    # is bound. Keep the contract check aware of those explicit mappings.
    $sourceAliases = @{}
    $partition = Get-Content -LiteralPath $definition -Raw
    [regex]::Matches($partition, '\{\{"([^\"]+)",\s*"([^\"]+)"\}\}') | ForEach-Object {
        $sourceAliases[$_.Groups[2].Value] = $_.Groups[1].Value
    }
    $missingColumns = $requiredColumns | Where-Object {
        ($_ -notin $headers) -and (($sourceAliases[$_] ?? $_) -notin $headers)
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

Write-Output 'Power BI source contract passed.'
