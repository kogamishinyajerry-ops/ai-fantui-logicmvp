#!/usr/bin/env python3
"""Close P8 phase: update gate to Approved, add P7/P8 to Roadmap DB."""
import json, os, http.client, ssl

NOTION_VERSION = "2022-06-28"

class NotionClient:
    def __init__(self, token, *, timeout=60.0):
        self.token = token
        self.timeout = timeout
        self._connection = None

    def close(self):
        if self._connection:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def _get_connection(self):
        if self._connection is None:
            self._connection = http.client.HTTPSConnection("api.notion.com", timeout=self.timeout)
        return self._connection

    def request(self, method, path, payload=None):
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
        }
        for attempt in range(2):
            conn = self._get_connection()
            try:
                conn.request(method, path, body=body, headers=headers)
                response = conn.getresponse()
                raw = response.read()
                text = raw.decode("utf-8", "replace")
                if 200 <= response.status < 300:
                    if not text.strip():
                        return {}
                    return json.loads(text)
                raise RuntimeError(f"Notion API failed: HTTP {response.status} {path}: {text}")
            except (http.client.HTTPException, OSError, ssl.SSLError) as err:
                self.close()
                if attempt == 0:
                    continue
                raise RuntimeError(f"Notion network error {path}: {err}") from err

    def query_database(self, database_id, filter_payload=None, sorts=None, page_size=100):
        payload = {"page_size": page_size}
        if filter_payload:
            payload["filter"] = filter_payload
        if sorts:
            payload["sorts"] = sorts
        return self.request("POST", f"/v1/databases/{database_id}/query", payload).get("results", [])

    def update_page_properties(self, page_id, properties):
        self.request("PATCH", f"/v1/pages/{page_id}", {"properties": properties})

    def create_page(self, database_id, properties):
        return self.request("POST", "/v1/pages", {
            "parent": {"database_id": database_id},
            "properties": properties,
        })

def title_value(text):
    return {"title": [{"text": {"content": text[:200]}}]}

def main():
    token = os.environ["NOTION_API_KEY"]
    client = NotionClient(token)

    config = json.load(open(".planning/notion_control_plane.json", "r"))
    gates_db = config["databases"]["gates"]
    roadmap_db = config["databases"]["roadmap"]

    # 1. Find and update the Gate to Approved
    print("=== Step 1: Update Gate to Approved ===")
    gate_rows = client.query_database(
        gates_db,
        filter_payload={"property": "Gate", "title": {"equals": "OPUS-4.6 周期审查 Gate"}}
    )
    for row in gate_rows:
        props = row.get("properties", {})
        status_prop = props.get("Status", {})
        current_status = (status_prop.get("select") or {}).get("name", "N/A")
        print(f"  Gate row: {row['id']}, current Status: {current_status}")
        if current_status != "Approved":
            client.update_page_properties(row["id"], {"Status": {"select": {"name": "Approved"}}})
            print(f"  -> Updated to Approved")
        else:
            print(f"  -> Already Approved, skipping")

    # 2. Update P6 from Active to Done, add P7 and P8 to Roadmap DB
    print("\n=== Step 2: Update P6, Add P7/P8 to Roadmap DB ===")
    roadmap_rows = client.query_database(roadmap_db, page_size=100)
    existing_rounds = {}  # round_name -> (page_id, current_status)
    for row in roadmap_rows:
        props = row.get("properties", {})
        round_name = "".join(t.get("plain_text", "") for t in props.get("Round", {}).get("title", []))
        status = (props.get("Status", {}).get("select") or {}).get("name", "N/A")
        existing_rounds[round_name] = (row["id"], status)
    print(f"  Existing rounds: {list(existing_rounds.keys())}")

    # Update P6 from Active to Done
    p6_key = None
    for k in existing_rounds:
        if k.startswith("P6"):
            p6_key = k
            break
    if p6_key:
        page_id, current_status = existing_rounds[p6_key]
        if current_status == "Active":
            client.update_page_properties(page_id, {"Status": {"select": {"name": "Done"}}})
            print(f"  P6 ({p6_key!r}): Updated from Active -> Done")
        else:
            print(f"  P6 ({p6_key!r}): Status is {current_status!r}, skipping")
    else:
        print("  P6 not found in Roadmap DB, skipping")

    phases_to_add = [
        ("P7", "Build A Spec-Driven Control Analysis Workbench"),
        ("P8", "Runtime Generalization Proof"),
    ]
    for phase_id, phase_name in phases_to_add:
        # Check if any existing round name starts with this phase_id
        found = False
        for existing_name in existing_rounds:
            if existing_name.startswith(phase_id):
                print(f"  {phase_id} already in Roadmap DB as {existing_name!r} (status={existing_rounds[existing_name][1]!r}), skipping")
                found = True
                break
        if found:
            continue
        print(f"  Adding {phase_id}: {phase_name}...")
        client.create_page(roadmap_db, {
            "Round": title_value(phase_id),
            "Status": {"select": {"name": "Done"}},
            "Goal": {"rich_text": [{"text": {"content": phase_name[:500]}}]},
        })
        print(f"  -> Added")

    client.close()
    print("\n=== P8 Phase Closure Complete ===")

if __name__ == "__main__":
    main()
