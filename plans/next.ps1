$s = Get-Content "$PSScriptRoot/state.json" | ConvertFrom-Json
$prompt = "Run the next action: $($s.build_id)-$($s.milestone_id)-$($s.phase_id) $($s.next_action_id)"
Set-Clipboard $prompt
Write-Output "$prompt  [copied]"
Write-Output "  (last: $($s.last_action.summary))"
