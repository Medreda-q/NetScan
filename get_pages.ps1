$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = "C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI_PERFECT.docx"
$doc = $word.Documents.Open($docPath)

Write-Host "Total Pages: " $doc.ComputeStatistics([Microsoft.Office.Interop.Word.WdStatistic]::wdStatisticPages)

for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $txt = $p.Range.Text.Trim()
    if ($txt.StartsWith("CHAPITRE") -or $txt.StartsWith("Introduction") -or $txt.StartsWith("Conclusion") -or $txt.StartsWith("Bibliographie") -or $txt.StartsWith("Table des")) {
        $page = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndPageNumber)
        Write-Host "P $page : $txt"
    }
}

$doc.Close([ref]$false)
$word.Quit()
