#!/usr/bin/env python3
"""Take screenshots through the DDEV Selenium container (W3C WebDriver + Chrome DevTools)."""
import base64, json, sys, time, urllib.request

HUB = 'http://selenium-chrome:4444'

def call(method, path, body=None):
    req = urllib.request.Request(HUB + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read() or b'{}').get('value')

class Browser:
    def __init__(self):
        v = call('POST', '/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {
            'args': ['--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage', '--hide-scrollbars']}}}})
        self.sid = v['sessionId']
    def cdp(self, cmd, params=None):
        return call('POST', f'/session/{self.sid}/goog/cdp/execute', {'cmd': cmd, 'params': params or {}})
    def viewport(self, width, height, mobile=False):
        self.cdp('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': mobile})
    def get(self, url, wait=1.5):
        call('POST', f'/session/{self.sid}/url', {'url': url}); time.sleep(wait)
    def js(self, script):
        return call('POST', f'/session/{self.sid}/execute/sync', {'script': script, 'args': []})
    def shot(self, path, full=True):
        params = {'format': 'png'}
        if full:
            h = self.js('return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)')
            w = self.js('return document.documentElement.clientWidth')
            params.update({'captureBeyondViewport': True, 'clip': {'x': 0, 'y': 0, 'width': w, 'height': min(h, 8000), 'scale': 1}})
        data = self.cdp('Page.captureScreenshot', params)['data']
        open(path, 'wb').write(base64.b64decode(data))
    def close(self):
        try: call('DELETE', f'/session/{self.sid}')
        except Exception: pass

if __name__ == '__main__':
    url, out, width, height = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    full = len(sys.argv) > 5 and sys.argv[5] == 'full'
    b = Browser()
    try:
        b.viewport(width, height, mobile=width < 600)
        b.get(url)
        print('title:', b.js('return document.title'))
        b.shot(out, full)
        print('saved', out)
    finally:
        b.close()
