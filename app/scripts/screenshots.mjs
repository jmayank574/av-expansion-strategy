// Capture the three app views for the README: node scripts/screenshots.mjs
// Starts the Vite dev server, drives the system Edge/Chrome through Playwright, writes ../docs/screenshots/*.png.
import { chromium } from 'playwright'
import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const out = path.resolve(here, '../../docs/screenshots')
const PORT = 5199
const base = `http://localhost:${PORT}/`

const server = spawn(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['vite', '--port', String(PORT), '--strictPort'], { cwd: path.resolve(here, '..'), shell: process.platform === 'win32', stdio: 'ignore' })
const stop = () => { try { process.platform === 'win32' ? spawn('taskkill', ['/pid', String(server.pid), '/t', '/f'], { stdio: 'ignore' }) : server.kill() } catch {} }

async function up() {
  for (let i = 0; i < 60; i++) { try { if ((await fetch(base)).ok) return } catch {} await new Promise(r => setTimeout(r, 500)) }
  throw new Error('dev server did not start')
}

let browser
try {
  await up()
  const channel = process.env.PW_CHANNEL ?? 'msedge'      // system browser: no Playwright browser download needed
  browser = await chromium.launch({ channel })
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5 })
  const shots = [['ranking', 'view=ranking', 'ranking.png'], ['quadrant', 'view=quadrant', 'quadrant.png'], ['drill', 'view=drill&metro=San%20Francisco', 'drilldown.png']]
  for (const [, qs, file] of shots) {
    await page.goto(`${base}?${qs}`)
    await page.waitForSelector('h1', { timeout: 15000 })
    await page.waitForTimeout(1200)                                   // let Recharts finish its animation
    await page.screenshot({ path: path.join(out, file), fullPage: true })
    console.log('saved', file)
  }
  // sanity: the Las Vegas drill-down shows operator presence and never names the operator
  await page.goto(`${base}?view=drill&metro=Las%20Vegas`)
  await page.waitForSelector('text=Operator presence', { timeout: 15000 })
  const body = await page.innerText('body')
  if (body.includes('Motional')) throw new Error('operator is named in the app')
  console.log('Las Vegas drill-down shows "Operator presence" and does not name the operator')
} finally {
  await browser?.close()
  stop()
}
