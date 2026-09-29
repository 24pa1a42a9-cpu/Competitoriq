import puppeteer from 'puppeteer-core';

const EDGE_PATH = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const APP_URL = 'http://localhost:5173';

async function testAnalyst() {
  const browser = await puppeteer.launch({ executablePath: EDGE_PATH, headless: true });
  const page = await browser.newPage();
  await page.goto(APP_URL);
  await new Promise(r => setTimeout(r, 1000));

  // Navigate to AI Analyst
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('aside.sidebar button'));
    const ai = btns.find(b => b.innerText.includes('AI Analyst'));
    if (ai) ai.click();
  });
  await new Promise(r => setTimeout(r, 1500));

  // Type question via puppeteer type
  const inputSelector = 'input[placeholder*="strategy evolved"]';
  await page.waitForSelector(inputSelector);
  await page.type(inputSelector, "How has Microsoft strategy evolved over time?");
  await new Promise(r => setTimeout(r, 500));

  // Click Run Query
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const runBtn = btns.find(b => b.innerText.includes('Run Query'));
    if (runBtn) {
      console.log('CLICKING RUN QUERY, DISABLED:', runBtn.disabled);
      runBtn.click();
    }
  });

  // Wait for result
  console.log('Waiting for AI Analyst answer...');
  let answered = false;
  for (let i = 0; i < 25; i++) {
    await new Promise(r => setTimeout(r, 1000));
    const text = await page.evaluate(() => document.body.innerText);
    if (text.includes('STRATEGIC SIGNAL') || text.includes('Strategic Signal') || text.includes('EVIDENCE') || text.includes('Inflection') || text.includes('Copilot')) {
      answered = true;
      console.log('ANSWER RECEIVED IN ' + (i + 1) + 's!');
      break;
    }
  }
  console.log('ANSWERED:', answered);
  await browser.close();
}

testAnalyst();
