[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$InputFile,
  [Parameter(Mandatory=$true)][string]$OutputFile
)
Import-Module ActiveDirectory -ErrorAction Stop
function Escape-LdapValue([string]$Value) {
  return $Value.Replace('\','\5c').Replace('*','\2a').Replace('(','\28').Replace(')','\29').Replace([string][char]0,'\00')
}
$results = foreach ($row in (Import-Csv -LiteralPath $InputFile)) {
  $email = ([string]$row.Email).Trim()
  if ([string]::IsNullOrWhiteSpace($email)) { throw 'Email vide dans le fichier' }
  $value = Escape-LdapValue $email
  $users = @(Get-ADUser -LDAPFilter "(|(mail=$value)(userPrincipalName=$value))" -Properties Enabled,LockedOut,LastLogonDate -ErrorAction Stop)
  if ($users.Count -eq 0) {
    [pscustomobject]@{Email=$email;Status='NOT_FOUND';SamAccountName='';Enabled='';LockedOut='';LastLogonDate=''}
  } elseif ($users.Count -gt 1) {
    [pscustomobject]@{Email=$email;Status='AMBIGUOUS';SamAccountName='';Enabled='';LockedOut='';LastLogonDate=''}
  } else {
    $user=$users[0]
    [pscustomobject]@{Email=$email;Status=$(if($user.Enabled){'ENABLED'}else{'DISABLED'});SamAccountName=$user.SamAccountName;Enabled=$user.Enabled;LockedOut=$user.LockedOut;LastLogonDate=$user.LastLogonDate}
  }
}
$parent=Split-Path -Parent $OutputFile
if ($parent -and -not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$results | Export-Csv -LiteralPath $OutputFile -NoTypeInformation -Encoding UTF8
$results | Group-Object Status | Select-Object Name,Count
