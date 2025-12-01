<div align="center">
  
# <img src="https://media.tenor.com/c4Bw2bvsu-YAAAAj/crown-gold.gif" width="50px" /> &nbsp;   **𝙉𝙚𝙫𝙚𝙧𝙊𝙛𝙛**  &nbsp; <img src="https://media.tenor.com/c4Bw2bvsu-YAAAAj/crown-gold.gif" width="50px" />
## sustains your account online 24/7 without any user-side application session

<p align="center">
  <a href="https://github.com/realAbdalrhman/NeverOFF/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/📜  License-GPLv3 🐧-orange?style=plastic&logo=gpl&logoColor=white" alt="License GPLv3 🐧">
  </a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://github.com/SealedSaucer/Online-Forever" target="_blank">
    <img src="https://img.shields.io/badge/_Based_On-ㅤ_🔗_ㅤ-lightgrey?style=plastic&logo=github&logoColor=white" alt="BasedOn ㅤ🔗ㅤ">
  </a>
</p>

<br>
    <img src="https://i.ibb.co/RTDzwjnd/X.png" height="320">
</div>

<hr>

  <br>
  
<div align="center">
  
## 🌟 Project Overview 
  </div>
  <br>
  
- **A fully autonomous _Discord presence bot script_**  
that **sustains your account online 24/7** without any user-side application session,  
operating as a **delegated presence layer** on your behalf.

- It orchestrates **continuous, protocol-accurate status injection** with  
**advanced custom states** and **comprehensive emoji support**  *custom, animated, or standard*   
granting **authoritative, fine-grained control** over your public activity signals.

- Fully compatible with **continuous 24/7 deployment** on cloud platforms such as  
**Replit**, **Render**, **Railway**, and other persistent hosting providers.

 <br>
 
<div align="center">
  
> ⚠️  **Disclaimer** ❗ 
>
> **By utilizing this code, you authorize automated activity on your Discord account**, a practice that **contravenes Discord’s Terms of Service and Community Guidelines** and, if not used properly, **may result in suspension or termination**. All associated risks rest solely with the user; **I, as a developer, assume no liability** for any consequences arising from its deployment. Proceed with full awareness and responsibility. **Learn more about** <a href="https://discord.com/terms">Discord's Terms of Service</a> **and** <a href="https://discord.com/guidelines">Community Guidelines</a>. 

> **This repository is entirely independent** and is neither affiliated with, endorsed by, nor formally recognized by Discord Inc. or any of its subsidiaries. _All references to Discord are solely for descriptive and interoperability purposes and do not imply sponsorship, authorization, or partnership._
</div>

<hr>

 <br>
<div align="center">
  
## 💡 Core Function & Features
  </div>
  <br>
  
* **Permanent Presence:** Keeps your desired custom status (`online`, `dnd`, `idle`) active 24/7.
* **Self-Healing Resilience:** Utilizes an **Exponential Backoff** reconnect strategy to manage network drops gracefully.
* **Critical Enhancement (v2.0):** Solved the infamous `AttributeError: 'WebSocket' object has no attribute 'close_code'` bug by implementing a **safe attribute access mechanism** (`getattr`), ensuring the bot never crashes due to common network timeouts or unexpected disconnections.
* **Heartbeat Integrity:** Incorporates **Advanced Heartbeat ACK Monitoring** to detect and proactively close "dead" connections faster than relying on simple timeouts.
* **Custom Emoji Support:** Full support for both **Unicode Emojis** and **Animated/Custom Server Emojis**.

<hr>

 <br>
<div align="center">
  
## 💻 Technology Stack
  </div>
  <br>
  
| Component | Purpose | Key Library |
| :--- | :--- | :--- |
| **Main Logic** | Discord Gateway Communication | `websocket-client` |
| **API Calls** | Token Validation | `requests` |
| **Uptime** | Cloud Host Health Check / Keep Alive | `Flask` |
| **Resilience** | Concurrency and Error Handling | `threading` / `try...except` |

<hr>

 <br>
<div align="center">
  
## 🚀 Deployment Guide: Setting Up on Any Host

  </div>
  <br>
  
- This guide explains how to configure and deploy the bot using **Environment Variables** (Env Vars), the standard and most secure way to run applications on cloud platforms like Railway, Render, or Heroku.

### 1. ⚙️ Required Environment Variables

You **must** set these variables in your hosting platform's configuration panel:

| Variable Name | Purpose | Example Value | Required? |
| :--- | :--- | :--- | :--- |
| `token` | **Your Discord User Token.** Keep this secret! | `Nz...MTU` | **YES** |
| `custom_status` | The text message for your custom status. | `𝙏𝙃𝙀 𝘽𝙀𝙎𝙏` | **YES** |

<br>

## 🔑 **Critical Step**: Obtaining Your Discord User *Token*

- **The `token` is the most crucial piece of data.** It acts as your passport to the Discord Gateway. Treat it with **extreme care** and never share it publicly.

<div align="center">
  
| 🛑 **IMPORTANT SECURITY & STABILITY NOTE** 🛑 |
| :--- |
| It is **highly recommended** to use a **temporary session token** obtained from a *private/incognito browsing window*. Once the bot successfully connects and runs on your permanent host, you can close the private browser session. This practice enhances security and ensures the host uses a clean, stable session separate from your main browser activity. |
</div>

<br>

### **Method 1**: The Fast Console Command (***Recommended***)

<br>

This method is the quickest and cleanest way to pull the token directly from your browser's console after logging into Discord.

1.  **Open Discord in your browser** and log in to the account you wish to control.
2.  Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac) to open the Developer Tools.
3.  Navigate to the **Console** tab.
4.  Copy the following JavaScript code and paste it into the console, then press `Enter`.

<details>
<summary>
<span style="color:#DAA520; font-weight:bold; font-size:16px;">📟 Click to reveal the Console Code Block</span>
</summary>
  
  ```javascript
// Function to find the token using Discord's internal structure
(function() {
    let token = null;
    
    // 1. Try to access the token via the Webpack stores
    try {
        const modules = webpackChunkdiscord_app.push([
            [Math.random().toString(36)], 
            {}, 
            e => e
        ]);
        
        // Search through all loaded modules for the 'getToken' function
        for (let i in modules.c) {
            let mod = modules.c[i].exports;
            if (mod && mod.default && mod.default.getToken) {
                let tokenResult = mod.default.getToken();
                
                // CRITICAL FIX: Check if the result is an object (like your previous error)
                if (typeof tokenResult === 'object' && tokenResult !== null) {
                    // Try to stringify the object and extract the token value
                    const tokenString = JSON.stringify(tokenResult);
                    // The token is often nested under a key, but sometimes just returned as a complex object.
                    // This often helps if the result is a complex object.
                    token = tokenString.match(/"(\w{24}\.\w{6}\.\w{27,})"/)?.[1]; 
                } else if (typeof tokenResult === 'string' && tokenResult.length > 50) {
                    token = tokenResult.replace(/"/g, '');
                }
                
                if (token) break;
            }
        }
    } catch (e) {
        // Fallback 1: Local Storage
        try {
            token = window.localStorage.getItem('token').replace(/"/g, '');
        } catch (err) {
            // Fallback 2: State Object
            for (const key in window) {
                if (key.startsWith('__OVERLAY_INITIAL_STATE')) {
                    token = JSON.parse(window[key]).auth.token;
                    break;
                }
            }
        }
    }

    if (token && token !== 'null' && token.length > 50) {
        console.log('%c✅ Discord User Token:', 'color: #38b2ac; font-size: 20px; font-weight: bold;');
        console.log('%c' + token, 'color: #ffffff; background-color: #2f3136; padding: 8px; border-radius: 5px; font-size: 16px;');
    } else {
        console.log('%c❌ Token Retrieval Failed:', 'color: #e53e3e; font-size: 20px; font-weight: bold;');
        console.log('Token not found using current console methods. Please use the Network tab method.');
    }
})();
```
</details> 

5.  **Copy the resulting long string** (which should be enclosed in quotes, e.g., `"Nz...MTU"`). This is your **`TOKEN`**.

<br>

### **Method 2**: Inspecting Network Traffic

<br>

**The traditional method for retrieving the token from the network headers.**

1.  **Open Discord in your browser** and open the Developer Tools (`F12`).
2.  Navigate to the **Network** tab.
3.  Click on any server or chat channel to initiate new network requests.
4.  In the Network filter box, type `api/v9` or `messages` and click on any request that appears (e.g., a message request).
5.  In the request details panel, find the **Headers** tab.
6.  Under **Request Headers**, locate the line starting with **`Authorization:`**.
7.  The long string following ` Authorization:  ` is your **`TOKEN`**. Copy this value.

-----
<br>

## 2. ✨ **Appearance Variables** (Optional Customization)

Use these variables to customize your status further. If not set, they use safe defaults.

#### A. Global Status (`STATUS`)

This controls the basic color/icon next to your name.

| Variable Name | Purpose | Possible Values | Default |
| :--- | :--- | :--- | :--- |
| `status` | The general status of your user account. | `online`, `dnd`, `idle` | `online` |

> ℹ️ **Note:** The value for **`status`** must be lowercase.

#### B. Emoji Configuration (Static or Animated)

You only need to set **`EMOJI_NAME`** for a simple Unicode emoji. For complex custom emojis (including animated ones), you must set all three related variables.

| Variable Name | Purpose | Example Value |
| :--- | :--- | :--- |
| `emoji_name` | The emoji name/text. | For Unicode: `🔥` or For Custom: `my_custom_emoji_name` |
| `emoji_id` | **Required for Custom Emojis.** The numerical ID of the emoji. | `1247965345034010728` |
| `emoji_animated` | Set to `True` if the custom emoji is animated. | `True` or `False` |

---

### 🔍 Detailed Guide: How to Get Custom Emoji IDs

To use a custom or animated emoji in your status, you need its unique ID.

1.  **Enable Developer Mode:** In Discord settings, go to **Advanced** and enable **Developer Mode**.
2.  **Get Emoji ID:**
    * Go to the server where the emoji is located.
    * Type the emoji in the chat with a backslash (`\`) before it.
        * Example: Type `\:emoji_name:`
    * The client will show the full ID string: `<:emoji_name:1234567890>` or `<a:emoji_name:1234567890>` (for animated).
    * The number at the end is the **Emoji ID**.

| Emoji Type | `emoji_name` value | `emoji_id` value | `emoji_animated` value |
| :--- | :--- | :--- | :--- |
| **Unicode** (e.g., 🚀) | `🚀` | `None` (leave blank) | `False` |
| **Static Custom** | `my_emoji` | `1234567890` | `False` |
| **Animated Custom** | `my_animated_emoji` | `1234567890` | `True` |

> ⚠️ **Discord Nitro Requirement:** To use **Animated Custom Emojis** (`emoji_animated` set to `True`) in your Custom Status, your user account **must** have an active Discord Nitro subscription. If you use an Animated Emoji without Nitro, Discord will typically downgrade it to a static image or remove it.

<hr>

<br>

<div align="center">
  
## 💻 Running Locally (Development/Testing)

  </div>
  <br>

  
- You can run this bot locally without relying on a cloud platform by using a local `.env` file for secure configuration and testing.

### 1. 💾 Installation and Setup Commands

You must install the necessary Python libraries. We will also install `python-dotenv` to correctly load variables from the local `.env` file.

<div align="left">
    
#### 📥 Required Installation Commands

| Action | Command |
| :--- | :--- |
| **Install Dependencies** | `pip install -r requirements.txt` |
| **Install Local Env Loader** | `pip install python-dotenv` |

</div>

### 2. 📝 Creating a Local `.env` File

Create a file named `.env` in the root directory of the project. This file securely holds your configuration, mirroring the structure of cloud environment variables.

<details>
<summary>Click to reveal Example <code>.env</code> Content</summary>

```bash
# .env file content
# =========================================================

# --- REQUIRED CONFIGURATION ---
TOKEN="YOUR_DISCORD_USER_TOKEN_HERE" 
custom_status="Always striving for perfection."

# --- OPTIONAL APPEARANCE ---
status="dnd" # Must be online, dnd, or idle

# Optional Emoji (Example: Animated Custom Emoji)
emoji_name="my_animated_emoji"
emoji_id="1234567890" 
emoji_animated="True" # Must be "True" or "False"
# =========================================================
````
</details> 

### 3\. ▶️ Launching the Client

For local execution to recognize the `.env` file, a small, one-time modification is required for `main.py`.

#### A. Modify `main.py` (One-Time Change)

Add the following lines **right after** the standard `import` statements at the very top of your `main.py` file:

```python
# Insert these lines in main.py after "import websocket" or "from keep_alive import keep_alive"
from dotenv import load_dotenv
load_dotenv() 
```

#### B. Execution Command

Execute the main script to start the self-healing client.

<div align="left">

#### ⚙️ Execution Command

| Action | Command |
| :--- | :--- |
| **Execute Client** | `python main.py` |

</div>

> ✅ The client will start, print the connection details, and begin its resilient, self-healing loop, ready to maintain your custom presence despite local network fluctuations.

<hr>

 <br>
 
<div align="center">

⭐️ **If this project proved valuable to you, consider starring the repository**

  </div>
  
  <br>
  
<hr>

<div align="center">
<strong style="color:#DAA520; font-size:16px;">[ @realAbdalrhman - 𝘼𝙆𝘼 ㅤ𝙏𝙃𝙀 / 𝘽𝙀𝙎𝙏 ]</strong> 
</div>

<div align="center">

[✘](https://x.com/realAbdalrhman)

</div>




<hr>
<hr>
<hr>
