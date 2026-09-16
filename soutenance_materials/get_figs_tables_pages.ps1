$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = "C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI_PERFECT.docx"
$doc = $word.Documents.Open($docPath)

Write-Host "=== FIGURES PAGES ==="
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $txt = $p.Range.Text.Trim()
    if ($txt -match "^Figure\s+5\.[1-7]") {
        $page = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndPageNumber)
        Write-Host "$page : $txt"
    }
    elseif ($txt -match "^Tableau\s+[1-5]\.[0-9]") {
        $page = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndPageNumber)
        Write-Host "$page : $txt"
    }
}

$doc.Close([ref]$false)
$word.Quit()
