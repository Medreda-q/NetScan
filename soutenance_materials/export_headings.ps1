$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = "C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI_PERFECT.docx"
$doc = $word.Documents.Open($docPath)

$headings = @()
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $style = $p.Style.NameLocal
    $txt = $p.Range.Text.Trim()
    if ($style -like "Titre*" -or $style -like "Heading*" -or $txt -match "^[1-9]\.") {
        $page = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndPageNumber)
        $headings += [PSCustomObject]@{
            Index = $i
            Page = $page
            Style = $style
            Text = $txt
        }
    }
}

$headings | Export-Csv -Path "headings_pages.csv" -NoTypeInformation -Encoding UTF8
Write-Host "Exported " $headings.Count " headings to headings_pages.csv"

$doc.Close([ref]$false)
$word.Quit()
