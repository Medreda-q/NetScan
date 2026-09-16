import docx
from docx.oxml import parse_xml

doc = docx.Document()

omml_cn = """
<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:r><m:t>c(n) = 2 </m:t></m:r>
    <m:d>
      <m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>
      <m:e>
        <m:r><m:t>ln(n - 1) + 0.5772156649</m:t></m:r>
      </m:e>
    </m:d>
    <m:r><m:t> - </m:t></m:r>
    <m:f>
      <m:fPr><m:type m:val="bar"/></m:fPr>
      <m:num><m:r><m:t>2(n - 1)</m:t></m:r></m:num>
      <m:den><m:r><m:t>n</m:t></m:r></m:den>
    </m:f>
  </m:oMath>
</m:oMathPara>
"""

omml_sxn = """
<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:r><m:t>s(x, n) = </m:t></m:r>
    <m:sSup>
      <m:e><m:r><m:t>2</m:t></m:r></m:e>
      <m:sup>
        <m:r><m:t>-</m:t></m:r>
        <m:f>
          <m:fPr><m:type m:val="bar"/></m:fPr>
          <m:num><m:r><m:t>E(h(x))</m:t></m:r></m:num>
          <m:den><m:r><m:t>c(n)</m:t></m:r></m:den>
        </m:f>
      </m:sup>
    </m:sSup>
  </m:oMath>
</m:oMathPara>
"""

omml_tw = """
<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:r><m:t>time_window = </m:t></m:r>
    <m:d>
      <m:dPr><m:begChr m:val="&#x230A;"/><m:endChr m:val="&#x230B;"/></m:dPr>
      <m:e>
        <m:f>
          <m:fPr><m:type m:val="bar"/></m:fPr>
          <m:num><m:r><m:t>Timestamp</m:t></m:r></m:num>
          <m:den><m:r><m:t>W</m:t></m:r></m:den>
        </m:f>
      </m:e>
    </m:d>
    <m:r><m:t> &#xD7; W</m:t></m:r>
  </m:oMath>
</m:oMathPara>
"""

p3 = doc.add_paragraph()
p3._p.append(parse_xml(omml_tw))
doc.save("test_out.docx")
print("Saved all 3 equations successfully!")


