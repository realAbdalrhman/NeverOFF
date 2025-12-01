import os
import sys
import json
import time
import threading
import traceback
import requests
import websocket
from keep_alive import keep_alive

# -----------------------
# Discord Gateway Opcodes Constants (لتحسين الوضوح)
# -----------------------
OP_DISPATCH = 0
OP_HEARTBEAT = 1
OP_IDENTIFY = 2
OP_PRESENCE_UPDATE = 3
OP_RESUME = 6
OP_RECONNECT = 7
OP_INVALID_SESSION = 9
OP_HELLO = 10
OP_HEARTBEAT_ACK = 11
ACTIVITY_TYPE_CUSTOM = 4

# -----------------------
# Configuration (env vars)
# -----------------------
STATUS = os.getenv("status", "online")
CUSTOM_STATUS = os.getenv("custom_status", "")
EMOJI_NAME = os.getenv("emoji_name", "")
EMOJI_ID = os.getenv("emoji_id", None)
# تحسين: تحويل المتغير البيئي إلى قيمة منطقية (True/False) بشكل آمن
EMOJI_ANIMATED = os.getenv("emoji_animated", "False").lower() == "true"
TOKEN = os.getenv("token")

# --- Simplified Configuration Check ---
# ضمان أن EMOJI_ID إما None أو قيمة صالحة
if EMOJI_ID is not None and EMOJI_ID.strip() == "":
    EMOJI_ID = None

# Basic token check
if not TOKEN:
    print("[ERROR] Missing environment variable: token. Please add your Discord user token.")
    sys.exit(1)

# Use canonical endpoint once to validate token
try:
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    # زمن مهلة قصيرة للتحقق
    resp = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
    
    if resp.status_code != 200:
        if resp.status_code == 401:
            print("[ERROR] Your token is INVALID (HTTP 401 Unauthorized). Please check the token value.")
        else:
            print("[ERROR] Failed to validate token (status code {}).".format(resp.status_code))
        sys.exit(1)
        
    userinfo = resp.json()
    USERNAME = userinfo.get("username", "unknown")
    DISCRIMINATOR = userinfo.get("discriminator", "0000")
    USERID = userinfo.get("id", "unknown")
except Exception as e:
    print(f"[ERROR] Token validation failed due to network or request error: {str(e)}")
    sys.exit(1)

# -----------------------
# Gateway client state
# -----------------------
GATEWAY_URL = "wss://gateway.discord.gg/?v=9&encoding=json"
session_id = None
sequence = None
ws = None
should_stop = threading.Event()
# متغير منطقي لحالة Heartbeat ACK (مهم للتحقق المتقدم)
last_ack = True 

# -----------------------
# Helper: build presence payload
# -----------------------
def build_presence_payload(status=STATUS, custom=CUSTOM_STATUS, emoji_name=EMOJI_NAME, emoji_id=EMOJI_ID, emoji_animated=EMOJI_ANIMATED):
    """Constructs the OP 3 PRESENCE_UPDATE payload."""
    
    # استخدام ثابت الـ Opcode
    activity = {
        "type": ACTIVITY_TYPE_CUSTOM, 
        "state": custom,
        "name": "Custom Status",
        "id": "custom"
    }
    
    # Attach emoji only if a name is provided
    if emoji_name:
        emoji_obj = {"name": emoji_name}
        if emoji_id:
            # Only include ID and animated flag if it's a CUSTOM emoji (has an ID)
            emoji_obj["id"] = emoji_id
            emoji_obj["animated"] = bool(emoji_animated)
        
        activity["emoji"] = emoji_obj

    payload = {
        "op": OP_PRESENCE_UPDATE,
        "d": {
            "since": 0,
            "activities": [activity],
            "status": status,
            "afk": False
        }
    }
    return payload

# -----------------------
# Core: connect, heartbeat, receive, reconnect
# -----------------------
def send_json(sock, obj):
    """A wrapper to send JSON data over the WebSocket."""
    try:
        sock.send(json.dumps(obj))
        return True
    except Exception:
        # socket may be closed; let outer loop handle
        return False

def handle_dispatch(data):
    """Handles incoming Gateway events (OP 0)."""
    global sequence, session_id
    # Update sequence for heartbeating and resuming
    if "s" in data and data["s"] is not None:
        sequence = data["s"]
        
    t = data.get("t")
    d = data.get("d")

    # Save session id on READY (T=READY)
    if t == "READY":
        session_id = d.get("session_id", session_id)
        print(f"✅ Session READY. Session ID: {session_id[:8]}...")

def open_gateway_and_run():
    """
    Persistent gateway connection with heartbeat thread and auto-resume/reconnect.
    """
    global ws, session_id, sequence, last_ack

    backoff = 1
    max_backoff = 60
    
    # Gateway Close Codes that require a session reset (OP 9)
    RESET_SESSION_CODES = [4004, 4010, 4011, 4012, 4013, 4014]

    while not should_stop.is_set():
        hb_thread = None
        try:
            print(f"[INFO] Attempting to connect to Gateway (Backoff: {backoff}s)...")
            
            # زيادة مهلة الاتصال لـ 10 ثوانٍ
            sock = websocket.create_connection(GATEWAY_URL, timeout=10) 
            ws = sock
            last_ack = True # Reset ACK state for new connection
            
            # --- 1. Receive HELLO (OP 10) ---
            hello_raw = sock.recv()
            hello = json.loads(hello_raw)
            if hello.get("op") != OP_HELLO or "d" not in hello:
                sock.close()
                raise RuntimeError("Unexpected HELLO payload.")

            heartbeat_interval_ms = hello["d"]["heartbeat_interval"]
            
            # --- 2. Start Heartbeat Thread ---
            hb_stop = threading.Event()
            hb_thread = threading.Thread(target=heartbeat_loop, args=(sock, heartbeat_interval_ms, hb_stop), daemon=True)
            hb_thread.start()

            # --- 3. Identify or Resume ---
            if session_id and sequence is not None:
                # Try resume (OP 6)
                resume_payload = {
                    "op": OP_RESUME,
                    "d": {
                        "token": TOKEN,
                        "session_id": session_id,
                        "seq": sequence
                    }
                }
                print("[INFO] Attempting to RESUME existing session.")
                send_json(sock, resume_payload)
            else:
                # Identify (OP 2) - Fresh connection
                identify_payload = {
                    "op": OP_IDENTIFY,
                    "d": {
                        "token": TOKEN,
                        "properties": {
                            "$os": "linux",
                            "$browser": "chrome",
                            "$device": "pc"
                        },
                        "presence": {"status": STATUS, "afk": False},
                        "compress": False,
                        "intents": 0 
                    }
                }
                print("[INFO] Sending IDENTIFY (new session).")
                send_json(sock, identify_payload)
                
                # --- 4. Set Custom Presence (OP 3) ---
                time.sleep(1) # Small pause to avoid racing with READY
                pres = build_presence_payload()
                send_json(sock, pres)

            # Reset backoff on successful connect/identify
            backoff = 1

            # --- 5. Receive Loop (blocking) ---
            while not should_stop.is_set():
                # التحقق من ACK قبل استقبال رسالة جديدة
                if not last_ack:
                    raise RuntimeError("Missed Heartbeat ACK. Connection is likely dead.")
                    
                try:
                    raw = sock.recv()
                    if not raw:
                        raise websocket.WebSocketConnectionClosedException("Received empty data.")
                    
                    data = json.loads(raw)
                    op = data.get("op")
                    
                    if op == OP_DISPATCH:
                        handle_dispatch(data)
                    elif op == OP_RECONNECT: 
                        raise RuntimeError("Gateway requested reconnect (OP 7).")
                    elif op == OP_INVALID_SESSION: 
                        resumable = data.get("d", False)
                        if not resumable:
                            session_id = None
                            sequence = None
                            print("[WARN] Non-resumable invalid session (OP 9). Resetting state.")
                        raise RuntimeError(f"Invalid session (OP 9): resumable={resumable}")
                    elif op == OP_HEARTBEAT_ACK:
                        # تحديث حالة ACK عند الاستلام
                        last_ack = True
                
                except websocket.WebSocketTimeoutException:
                    continue # Continue waiting
                except (websocket.WebSocketConnectionClosedException, ConnectionResetError) as e:
                    raise RuntimeError(f"WebSocket closed: {e}")
                
        except Exception as exc:
            # استخدام getattr للوصول الآمن لـ close_code
            close_code = getattr(ws, "close_code", None) if ws else None
            
            # Handle specific close codes first
            if isinstance(exc, websocket.WebSocketException) and close_code:
                if close_code in RESET_SESSION_CODES:
                    session_id = None
                    sequence = None
                    print(f"[FATAL] Gateway error {close_code}: Unrecoverable session error. Resetting state.")
                else:
                    print(f"[WARN] Gateway closed with code {close_code}.")
            
            # Clean up socket and heartbeat thread
            if hb_thread:
                hb_stop.set()
                hb_thread.join(timeout=2)
            try:
                if ws: ws.close()
            except Exception:
                pass
            
            # Log and backoff
            err_text = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            print(f"[WARN] Gateway error: {err_text}. Reconnecting in {backoff}s.")
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)
            continue

def heartbeat_loop(sock, interval_ms, stop_event: threading.Event):
    """
    Sends heartbeats (OP 1) based on the interval from the HELLO payload.
    """
    global sequence, last_ack
    interval = interval_ms / 1000.0
    
    while not stop_event.is_set():
        # Sleep for the interval, allowing for an early stop
        # نستخدم stop_event.wait بدلاً من time.sleep المجزأة لتكون أكثر نظافة
        if stop_event.wait(interval):
            return

        try:
            # 1. التحقق من ACK (إذا كان FALSE فهذا يعني فشل Heartbeat السابق)
            if not last_ack:
                # إذا لم يتم تلقي ACK، فإننا لن نرسل Heartbeat آخر، وسندع Main loop يكتشف المشكلة
                # (سيكتشفها في بداية حلقة الاستقبال ويقوم بفصل الاتصال وإعادة الاتصال)
                continue
                
            # 2. إعداد Heartbeat
            hb_payload = {"op": OP_HEARTBEAT, "d": sequence}
            
            # 3. إرسال Heartbeat وتعيين ACK إلى False
            if send_json(sock, hb_payload):
                last_ack = False # نتوقع ACK قبل Heartbeat التالي
            else:
                # If send fails, exit the heartbeat loop
                return
        except Exception:
            return

# -----------------------
# Entrypoint
# -----------------------
def main():
    print(f"✅ Logged in as: {USERNAME}#{DISCRIMINATOR} ({USERID}).")
    print(f"Configuration: Status='{STATUS}', Custom='{CUSTOM_STATUS}', Emoji='{EMOJI_NAME}'")
    
    # Start keep_alive web server for cloud-host healthchecks
    keep_alive()

    # Start gateway thread (persistent connection)
    gw_thread = threading.Thread(target=open_gateway_and_run, daemon=True)
    gw_thread.start()

    # Main thread: keep alive until stopped
    try:
        while True:
            time.sleep(60) # Main thread sleeps, letting the daemon threads run
    except KeyboardInterrupt:
        should_stop.set()
        print("\nShutting down by user request...")
        # Give the gateway thread a moment to clean up
        gw_thread.join(timeout=5)
        sys.exit(0)

if __name__ == "__main__":
    main()
