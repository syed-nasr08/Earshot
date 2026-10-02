/**
 * Interview Helper — Google Doc sink (Apps Script web app)
 *
 * SETUP (one time, ~5 min):
 *   1. Open the Google Doc you want answers written to.
 *   2. Extensions -> Apps Script. Delete any sample code.
 *   3. Paste this whole file in. Change SECRET below to any phrase you like.
 *   4. Click Deploy -> New deployment.
 *        - Type: Web app
 *        - Execute as: Me
 *        - Who has access: Anyone
 *      Authorize when prompted (you may see an "unverified app" screen ->
 *      Advanced -> Go to <project> (unsafe); it's your own script).
 *   5. Copy the Web app URL (ends in /exec).
 *   6. In the app's .env file set:
 *        GDOC_WEBAPP_URL=<that /exec URL>
 *        GDOC_SECRET=<the same SECRET you set below>
 *
 * The script writes to whatever doc it is bound to (the one you opened in
 * step 1), so no document ID is needed.
 */

const SECRET = 'change-me-to-a-secret';  // must match GDOC_SECRET in .env

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    if (data.secret !== SECRET) {
      return _json({ ok: false, error: 'bad secret' });
    }

    const body = DocumentApp.getActiveDocument().getBody();

    if (data.action === 'clear') {
      body.clear();
      return _json({ ok: true, cleared: true });
    }

    // append
    if (data.question) {
      body.appendParagraph('Q: ' + data.question).editAsText().setBold(true);
    }
    if (data.answer) {
      body.appendParagraph('A: ' + data.answer).editAsText().setBold(false);
    }
    body.appendParagraph('');
    return _json({ ok: true });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
