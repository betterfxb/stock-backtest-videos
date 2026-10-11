param([string[]]$Targets = @("300308:1","002463:0","300502:0","688981:1","688012:1","002371:0","002415:0","300750:0"))

# NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads .ps1 as ANSI
# when there is no BOM, which mangles any non-ASCII literals (stock names).
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$all = @{}

foreach ($t in $Targets) {
    $parts = $t.Split(":")
    $code = $parts[0]; $market = $parts[1]
    $url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=$market.$code&fields1=f1,f2&fields2=f51,f53&klt=103&fqt=1&beg=20200101&end=20500101"
    try {
        $j = (Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30).Content | ConvertFrom-Json
        $k = $j.data.klines
        if ($k -and $k.Count -gt 12) {
            $rows = @()
            foreach ($line in $k) {
                $p = $line.Split(",")
                $rows += @{ date = $p[0]; close = [double]$p[1] }
            }
            $all["$code"] = @{ code = $code; market = $market; rows = $rows }
            Write-Output ("{0}: {1} months  {2} ~ {3}" -f $code, $rows.Count, $rows[0].date, $rows[-1].date)
        } else { Write-Output "$code insufficient" }
    } catch { Write-Output "$code ERR: $($_.Exception.Message)" }
    Start-Sleep -Milliseconds 900
}

$outFile = Join-Path $dir "klines_all.json"
$all | ConvertTo-Json -Depth 6 -Compress | Set-Content -Path $outFile -Encoding UTF8
Write-Output "saved $outFile ($($all.Count) symbols)"