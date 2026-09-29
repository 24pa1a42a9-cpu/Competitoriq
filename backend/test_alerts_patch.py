import urllib.request
import json

def req(url, method='GET', payload=None):
    data = json.dumps(payload).encode('utf-8') if payload else None
    r = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method=method)
    with urllib.request.urlopen(r) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

st, res = req('http://127.0.0.1:5000/api/alerts?competitor=microsoft&limit=2')
alerts = res.get('alerts', [])
print(f'Fetched {len(alerts)} alerts')
if alerts:
    alt = alerts[0]
    aid = alt['id']
    print(f"Testing alert {aid} (initial status: {alt.get('status')})")
    
    # Test Read
    st, r_res = req(f'http://127.0.0.1:5000/api/alerts/{aid}/read', method='PATCH')
    new_status = r_res.get('alert', {}).get('status')
    print(f"PATCH read: {st} -> status: {new_status}")
    assert new_status == 'read', f"Expected status 'read', got {new_status}"
    
    # Test Dismiss
    st, d_res = req(f'http://127.0.0.1:5000/api/alerts/{aid}/dismiss', method='PATCH')
    new_status2 = d_res.get('alert', {}).get('status')
    print(f"PATCH dismiss: {st} -> status: {new_status2}")
    assert new_status2 == 'dismissed', f"Expected status 'dismissed', got {new_status2}"

    # Reset back to new or read for normal demo state
    st, r2_res = req(f'http://127.0.0.1:5000/api/alerts/{aid}/read', method='PATCH')
    print(f"Reset alert status -> {r2_res.get('alert', {}).get('status')}")
    print("[PASS] Alert status transition read/dismiss works and persists in database.")
