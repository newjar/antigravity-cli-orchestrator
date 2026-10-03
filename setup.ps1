# Interactive project setup for Antigravity (agy)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host @'
+---------------------------------------+
|    _    ______   __                   |
|   / \  / ___\ \ / /                   |
|  / _ \| |  _ \ V /                    |
| / ___ \ |_| | | |                     |
|/_/   \_\____| |_|                     |
|                                       |
|       O R C H E S T R A T O R         |
|       Choose models per role.         |
|    Configure Antigravity (agy).       |
+---------------------------------------+
'@

Write-Host "Interactive project setup for Antigravity (agy)"
$TargetPath = Read-Host "Target repository path"

if ([string]::IsNullOrWhiteSpace($TargetPath) -or -not (Test-Path $TargetPath -PathType Container)) {
    Write-Error "Target must be an existing directory: $TargetPath"
    exit 1
}

$TargetDir = (Resolve-Path $TargetPath).Path
if ($TargetDir -eq $ScriptDir) {
    Write-Error "Target repository must be different from the setup source directory."
    exit 1
}

function Confirm-Action($Prompt, $DefaultYes = $true) {
    $suffix = if ($DefaultYes) { "[Y/n]" } else { "[y/N]" }
    while ($true) {
        $ans = Read-Host "$Prompt $suffix"
        if ([string]::IsNullOrWhiteSpace($ans)) {
            return $DefaultYes
        }
        if ($ans -match '^(y|yes)$') { return $true }
        if ($ans -match '^(n|no)$') { return $false }
        Write-Host "Please answer yes or no."
    }
}

$ModelCatalog = @{
    "1"  = "gemini-3.8-flash-high"
    "2"  = "gemini-3.8-flash-medium"
    "3"  = "gemini-3.8-flash-low"
    "4"  = "claude-opus-5-5-high"
    "5"  = "claude-opus-5-5-medium"
    "6"  = "claude-opus-5-5-low"
    "7"  = "claude-sonnet-5-5-high"
    "8"  = "claude-sonnet-5-5-medium"
    "9"  = "claude-sonnet-5-5-low"
}

Write-Host "`nAvailable Antigravity Models (Gemini 3.8 & Claude 5.5):"
Write-Host "  1)  gemini-3.8-flash-high      (Gemini 3.8 Flash - High)"
Write-Host "  2)  gemini-3.8-flash-medium    (Gemini 3.8 Flash - Medium)"
Write-Host "  3)  gemini-3.8-flash-low       (Gemini 3.8 Flash - Low)"
Write-Host "  4)  claude-opus-5-5-high       (Claude Opus 5.5 - High)"
Write-Host "  5)  claude-opus-5-5-medium     (Claude Opus 5.5 - Medium)"
Write-Host "  6)  claude-opus-5-5-low        (Claude Opus 5.5 - Low)"
Write-Host "  7)  claude-sonnet-5-5-high     (Claude Sonnet 5.5 - High)"
Write-Host "  8)  claude-sonnet-5-5-medium   (Claude Sonnet 5.5 - Medium)"
Write-Host "  9)  claude-sonnet-5-5-low      (Claude Sonnet 5.5 - Low)"
Write-Host "  10) custom                     (Enter custom model ID)"

function Select-RoleModel($RoleName, $DefaultModel) {
    while ($true) {
        $ans = Read-Host "Model for $RoleName [$DefaultModel]"
        if ([string]::IsNullOrWhiteSpace($ans)) {
            return $DefaultModel
        }
        if ($ans -eq "10" -or $ans -eq "custom") {
            $custom = Read-Host "Enter custom model ID"
            return $custom
        }
        if ($ModelCatalog.ContainsKey($ans)) {
            return $ModelCatalog[$ans]
        }
        return $ans
    }
}

function Select-Concurrency($DefaultVal = "4") {
    while ($true) {
        $ans = Read-Host "Maximum concurrent subagents [$DefaultVal]"
        if ([string]::IsNullOrWhiteSpace($ans)) {
            return $DefaultVal
        }
        if ($ans -match '^[1-9][0-9]*$') {
            return $ans
        }
        Write-Host "Enter a positive integer without leading zeroes."
    }
}

$RootModel = Select-RoleModel "root / orchestrator" "claude-sonnet-5-5-high"
$DefaultSubModel = Select-RoleModel "default subagent" "gemini-3.8-flash-high"
$ExplorerModel = Select-RoleModel "explorer" "gemini-3.8-flash-high"
$WorkerModel = Select-RoleModel "worker" "claude-sonnet-5-5-high"
$TesterModel = Select-RoleModel "tester" "gemini-3.8-flash-high"
$ReviewerModel = Select-RoleModel "reviewer" "claude-sonnet-5-5-high"
$ResearcherModel = Select-RoleModel "researcher" "gemini-3.8-flash-high"
$Concurrency = Select-Concurrency "4"

Write-Host "`nSelected configuration:"
Write-Host "  root / orchestrator:   $RootModel"
Write-Host "  default subagent:      $DefaultSubModel"
Write-Host "  explorer:              $ExplorerModel"
Write-Host "  worker:                $WorkerModel"
Write-Host "  tester:                $TesterModel"
Write-Host "  reviewer:              $ReviewerModel"
Write-Host "  researcher:            $ResearcherModel"
Write-Host "  max subagents:         $Concurrency"

Write-Host "`nComponent installation:"
$InstallAgy = Confirm-Action "Install .agy role configuration (.agy/config.toml and agents/*.toml)?" $true
$InstallSkill = Confirm-Action "Install agy-orchestrator skill (.agents/skills/agy-orchestrator/)?" $true
$InstallRules = Confirm-Action "Install orchestration rules (GEMINI.md)?" $true

function Set-TomlValue($FilePath, $Key, $Value, $IsString = $true) {
    $content = Get-Content $FilePath -Raw
    $pattern = "(?m)^$Key\s*=.*$"
    $replacement = if ($IsString) { "$Key = `"$Value`"" } else { "$Key = $Value" }
    $updated = [regex]::Replace($content, $pattern, $replacement)
    Set-Content -Path $FilePath -Value $updated -NoNewline
}

if ($InstallAgy) {
    $targetAgy = Join-Path $TargetDir ".agy"
    $targetAgents = Join-Path $targetAgy "agents"
    if (-not (Test-Path $targetAgents)) {
        New-Item -ItemType Directory -Path $targetAgents -Force | Out-Null
    }

    Copy-Item (Join-Path $ScriptDir "templates/agy/config.toml") (Join-Path $targetAgy "config.toml") -Force
    foreach ($r in @("explorer", "worker", "tester", "reviewer", "researcher")) {
        Copy-Item (Join-Path $ScriptDir "templates/agy/agents/$r.toml") (Join-Path $targetAgents "$r.toml") -Force
    }

    $configFile = Join-Path $targetAgy "config.toml"
    Set-TomlValue $configFile "model" $RootModel $true
    Set-TomlValue $configFile "default_subagent_model" $DefaultSubModel $true
    Set-TomlValue $configFile "max_concurrent_threads_per_session" $Concurrency $false

    Set-TomlValue (Join-Path $targetAgents "explorer.toml") "model" $ExplorerModel $true
    Set-TomlValue (Join-Path $targetAgents "worker.toml") "model" $WorkerModel $true
    Set-TomlValue (Join-Path $targetAgents "tester.toml") "model" $TesterModel $true
    Set-TomlValue (Join-Path $targetAgents "reviewer.toml") "model" $ReviewerModel $true
    Set-TomlValue (Join-Path $targetAgents "researcher.toml") "model" $ResearcherModel $true

    Write-Host "Installed .agy configuration to $targetAgy"
}

if ($InstallSkill) {
    $skillSrc = Join-Path $ScriptDir ".agents/skills/agy-orchestrator"
    $skillDst = Join-Path $TargetDir ".agents/skills/agy-orchestrator"
    if (-not (Test-Path $skillDst)) {
        New-Item -ItemType Directory -Path $skillDst -Force | Out-Null
    }
    Copy-Item (Join-Path $skillSrc "SKILL.md") (Join-Path $skillDst "SKILL.md") -Force
    Write-Host "Installed agy-orchestrator skill to $skillDst"
}

if ($InstallRules) {
    $geminiTarget = Join-Path $TargetDir "GEMINI.md"
    $ruleContent = Get-Content (Join-Path $ScriptDir "templates/GEMINI.md") -Raw

    if (Test-Path $geminiTarget) {
        $existing = Get-Content $geminiTarget -Raw
        if ($existing -match "agy-orchestrator") {
            Write-Host "Orchestrator instructions already present in $geminiTarget"
        } else {
            Add-Content -Path $geminiTarget -Value "`n`n$ruleContent"
            Write-Host "Appended orchestrator instructions to $geminiTarget"
        }
    } else {
        Set-Content -Path $geminiTarget -Value $ruleContent
        Write-Host "Created $geminiTarget"
    }
}

Write-Host "`nSetup complete! You can now use Antigravity (agy) in $TargetDir with agy-orchestrator."
