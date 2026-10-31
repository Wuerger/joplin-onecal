# joplin-onecal

A lightweight, self-hostable Progressive Web App (PWA) that provides a **OneCalendar-style floating calendar view** for [Joplin Desktop](https://joplinapp.org/).

Designed to work with **End-to-End Encryption (E2EE)**: the container serves only static client-side assets (`index.html`, `manifest.json`, `icon.svg`, `sw.js`), while your browser connects directly to the local Joplin Desktop Web Clipper API (`http://127.0.0.1:41184`) on whichever computer you are using.

## Features

- **E2EE-Compatible & Zero Server State**: No notes or tokens are ever sent to the server. Each computer pairs with its own local Joplin Desktop instance and stores its Web Clipper token in browser `localStorage`.
- **Genuine Modification Tracking**: Queries Joplin's `/search` and `/revisions` APIs to filter out view-only formatting/line-ending (`\r\n`) auto-saves triggered when opening notes in Joplin's Rich Text editor.
- **Modified or Created View**: Switch between viewing notes by last modified date or creation date in `⚙️` Settings.
- **1-Click Open in Joplin**: Clicking any note on the calendar opens it directly in your running Joplin Desktop client (`joplin://x-callback-url/openNote?id=...`) across Windows, macOS, and Linux.
- **Installable PWA & Offline Support**: Includes a Web App Manifest and Service Worker (`sw.js`) so it can be installed as a standalone desktop window and continues working offline.

---

## Quick Start (Docker Compose)

```yaml
services:
  joplin-onecal:
    image: ghcr.io/wuerger/joplin-onecal:latest
    container_name: joplin-onecal
    restart: unless-stopped
    ports:
      - "8085:80"
```

---

## Setup on Each Computer (Windows, macOS, Linux)

1. **Enable Joplin Web Clipper**:
   - Open **Joplin Desktop** on your computer.
   - Go to **Tools → Options → Web Clipper** (Windows/Linux) or **Joplin → Settings → Web Clipper** (macOS).
   - Enable the Web Clipper service and copy the **Authorization token** under **Advanced options**.
2. **Connect the Calendar**:
   - Open your hosted `joplin-onecal` URL in **Chrome**, **Edge**, **Brave**, or **Firefox**.
   - Click **`⚙️`** (top right), paste your **Authorization Token**, click **`🔌 Test Connection`**, and click **`Save`**.
3. **Install as a Floating Desktop App (PWA)**:
   - Click **`⬇ Install`** in the top-right toolbar (or the install icon in your browser's address bar) to run `joplin-onecal` in its own standalone window.

### Browser Notes for `https://` Hosting

Because the hosted `https://` web app communicates with your local Joplin client on `http://127.0.0.1:41184`:
- **Chrome / Edge**: Allow the one-time *"Allow this site to access devices on your local network?"* prompt if shown.
- **Brave**: Click the Brave lion icon in the address bar and set **Brave Shields Down** for this domain so loopback requests to `127.0.0.1` are permitted.
- **macOS**: Install and run the PWA using **Chrome, Brave, or Edge** (Safari blocks `https://` pages from querying `http://127.0.0.1`).

