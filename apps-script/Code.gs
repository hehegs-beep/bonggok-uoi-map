const SHEET_ID = '18_ZA6uaC1YJq5xwXqs3c8XGuQ3gamQMg0MINzBC0FMk';
const TOPICS = ['우리는 누구인가','우리가 속한 공간과 시간','우리 자신을 표현하는 방법','세계가 돌아가는 방식','우리 자신을 조직하는 방식','우리 모두의 지구'];
function sheet_() { return SpreadsheetApp.openById(SHEET_ID).getSheetById(0); }
function doGet(e) {
  const template = HtmlService.createTemplateFromFile('Editor');
  template.code = String(e.parameter.code || '');
  template.channel = String(e.parameter.channel || '');
  return template.evaluate().setTitle('UOI 주제 수정').setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
function listMappings(code) {
  if (!/^[0-9가-힣A-Za-z-]+$/.test(code)) throw new Error('성취기준 코드를 확인해 주세요.');
  const rows = sheet_().getDataRange().getDisplayValues();
  return { topics: TOPICS, rows: rows.slice(1).map((r,i)=>({row:i+2, identity:JSON.stringify(r.slice(0,6)), subject:r[0], semester:r[2], unit:r[3], standard:r[5], value:r[6]})).filter(r=>r.standard.startsWith('['+code+']')) };
}
function saveMapping(payload) {
  const lock = LockService.getScriptLock();
  lock.waitLock(15000);
  try {
    if (!Number.isInteger(payload.row) || payload.row < 2) throw new Error('행 번호가 올바르지 않습니다.');
    const sheet = sheet_();
    const current = sheet.getRange(payload.row,1,1,7).getDisplayValues()[0];
    if (JSON.stringify(current.slice(0,6)) !== payload.identity || current[6] !== payload.previous) throw new Error('다른 사람이 수정했거나 행 위치가 바뀌었습니다. 새로 불러온 뒤 다시 수정해 주세요.');
    if (!Array.isArray(payload.topics) || payload.topics.some(t=>!TOPICS.includes(t))) throw new Error('주제를 확인해 주세요.');
    const value = [...new Set(payload.topics)].join('\n');
    sheet.getRange(payload.row,7).setValue(value);
    SpreadsheetApp.flush();
    return value;
  } finally { lock.releaseLock(); }
}
