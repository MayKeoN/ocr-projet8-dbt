# Create GitHub repo and push projet8_ocr (run after: gh auth login)
param(
    [string]$RepoName = "ocr-projet8-dbt",
    [ValidateSet("public", "private")]
    [string]$Visibility = "private"
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

$gh = Get-Command gh -EA SilentlyContinue
if (-not $gh) {
    $cached = Get-ChildItem "$env:TEMP\gh-cli" -Recurse -Filter gh.exe -EA SilentlyContinue | Select-Object -First 1
    if ($cached) { $gh = $cached.FullName } else { throw "Install GitHub CLI: https://cli.github.com/ or re-run agent setup" }
} else { $gh = $gh.Source }

Push-Location $root
try {
    & $gh auth status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Run first: gh auth login"
        & $gh auth login
    }

    git branch -M main 2>$null

    $exists = & $gh repo view $RepoName 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating repo: $RepoName ($Visibility)"
        & $gh repo create $RepoName --$Visibility --source=. --remote=origin --description "OCR Projet 8 - dbt pipeline sociodemographic analysis (Snowflake)" --push
    } else {
        Write-Host "Repo exists, pushing..."
        git remote remove origin 2>$null
        $user = (& $gh api user -q .login)
        git remote add origin "https://github.com/$user/$RepoName.git"
        git push -u origin main
    }

    $url = & $gh repo view $RepoName --json url -q .url
    Write-Host "Done: $url"
} finally {
    Pop-Location
}
