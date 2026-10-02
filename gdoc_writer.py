"""Writes questions and answers into a Google Doc via an Apps Script web app.

The Apps Script (see google_apps_script.gs) is deployed as a web app that
accepts a JSON POST and appends to / clears the bound document. This keeps the
Python side dependency-free of Google auth libraries.
"""
import threading

import httpx

from config import GDOC_SECRET, GDOC_WEBAPP_URL


class GoogleDocWebAppWriter:
    def __init__(self):
        if not GDOC_WEBAPP_URL:
            raise RuntimeError("GDOC_WEBAPP_URL is not set.")
        self.url = GDOC_WEBAPP_URL
        self.secret = GDOC_SECRET
        self._lock = threading.Lock()
        # Apps Script responds via a 302 redirect, so follow_redirects is required.
        self._client = httpx.Client(follow_redirects=True, timeout=30.0)

    def _post(self, payload: dict) -> dict:
        payload["secret"] = self.secret
        resp = self._client.post(self.url, json=payload)
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(
                "Apps Script did not return JSON — check the deployment is a "
                "Web App with access set to 'Anyone'."
            )
        if not data.get("ok"):
            raise RuntimeError(f"Apps Script error: {data.get('error')}")
        return data

    def append(self, question: str, answer: str):
        with self._lock:
            self._post({"action": "append", "question": question, "answer": answer})

    def clear(self):
        with self._lock:
            self._post({"action": "clear"})
        print("\n[F9] Google Doc cleared — fresh session.\n")
