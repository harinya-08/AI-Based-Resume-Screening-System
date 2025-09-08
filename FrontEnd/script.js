const heading = document.getElementById("myID1");
const headingText = "Is your resume good enough?";
let headingIndex = 0;
function typeHeading() {
  if (headingIndex < headingText.length) {
    heading.innerHTML += headingText.charAt(headingIndex);
    headingIndex++;
    setTimeout(typeHeading, 80);
  }
}
const para = document.getElementById("myID2");
const paraText = `An AI Powered Resume Scan helps\n
you to optimize your Resume for any\n
Job highlighting the key experience\n
and skills that recruiters need to see.`;

let paraIndex = 0;
let paraDisplay = '';
function typePara() {
  if (paraIndex < paraText.length) {
    if (paraText.charAt(paraIndex) === '\n') {
      paraDisplay += '<br>';
    } else {
      paraDisplay += paraText.charAt(paraIndex);
    }
    para.innerHTML = paraDisplay;
    paraIndex++;
    setTimeout(typePara, 30);
  }
}
typeHeading();
setTimeout(typePara, headingText.length * 80 + 500);
