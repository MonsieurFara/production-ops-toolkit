[CmdletBinding(SupportsShouldProcess=$true,ConfirmImpact='High')]
param(
  [Parameter(Mandatory=$true)][string]$InputFile,
  [switch]$Execute,
  [string]$BackupDirectory='.\output'
)
Import-Module ActiveDirectory -ErrorAction Stop
$plan=@()
$identities=[System.Collections.Generic.HashSet[string]]::new()
foreach ($row in (Import-Csv -LiteralPath $InputFile)) {
  if ([string]::IsNullOrWhiteSpace($row.Identity)) { throw 'Identity vide' }
  if ($row.Action -notin @('Enable','Disable')) { throw 'Action attendue : Enable ou Disable' }
  if ([string]::IsNullOrWhiteSpace($row.ChangeReference)) { throw 'Référence de changement requise' }
  $account=Get-ADUser -Identity $row.Identity -Properties Enabled -ErrorAction Stop
  if (-not $identities.Add($account.ObjectGuid.ToString())) { throw 'Compte présent plusieurs fois dans le plan' }
  $plan += [pscustomobject]@{Identity=$account.SamAccountName;CurrentEnabled=$account.Enabled;Action=$row.Action;ChangeReference=$row.ChangeReference;ObjectGuid=$account.ObjectGuid}
}
$plan | Select-Object Identity,CurrentEnabled,Action,ChangeReference | Format-Table
if (-not $Execute) { Write-Output 'Simulation : aucun état AD modifié'; return }
if (-not (Test-Path -LiteralPath $BackupDirectory)) { New-Item -ItemType Directory -Path $BackupDirectory | Out-Null }
$backup=Join-Path $BackupDirectory ('ad-before-'+(Get-Date -Format 'yyyyMMddTHHmmss')+'.csv')
$plan | Export-Csv -LiteralPath $backup -NoTypeInformation -Encoding UTF8
foreach ($item in $plan) {
  if ($PSCmdlet.ShouldProcess($item.Identity,$item.Action+' AD account')) {
    if ($item.Action -eq 'Enable') { Enable-ADAccount -Identity $item.ObjectGuid -ErrorAction Stop }
    else { Disable-ADAccount -Identity $item.ObjectGuid -ErrorAction Stop }
    $after=Get-ADUser -Identity $item.ObjectGuid -Properties Enabled -ErrorAction Stop
    $expected=($item.Action -eq 'Enable')
    if ($after.Enabled -ne $expected) { throw 'État obtenu différent du plan' }
  }
}
