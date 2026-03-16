# ai-calendar-plugin

Personal calendar assistant for Claude Code. Manage your Google Calendar schedule and track daily activities with `/schedule`, `/track`, and `/review` commands.

## Commands

| Command | Description |
|---------|-------------|
| `/schedule` | Register discussed events, view schedule, edit/delete events |
| `/track` | Time tracking — start/stop activity timers, view today's log |
| `/review` | Smart daily briefing (morning plan / evening review / midday check) |

## Setup

### 1. Clone

```bash
git clone https://github.com/kdmin3318/ai-calendar-plugin
cd ai-calendar-plugin
```

### 2. Install server dependencies

```bash
pip install -r server/requirements.txt
```

Or with `uv`:

```bash
uv pip install -r server/requirements.txt
```

### 3. Get Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Google Calendar API**
3. Create **OAuth 2.0 Client ID** (Desktop app type)
4. Download as `credentials.json` and place it in the plugin root

### 4. First run — browser authentication

On first use, a browser window will open for Google OAuth consent.
After approval, `token.json` is saved automatically (no re-auth needed).

### 5. Start Claude Code

Open Claude Code in the plugin directory. The `.mcp.json` will register the MCP server automatically.

```bash
claude
```

### 6. Use commands

```
/schedule          # View today's schedule
/track start 코드 작성   # Start tracking an activity
/track stop        # Stop current activity
/review            # Get smart briefing based on time of day
```

## Configuration

Edit `.mcp.json` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `CREDENTIALS_PATH` | `credentials.json` | OAuth credentials file path |
| `TOKEN_PATH` | `token.json` | Saved token file path |
| `TIMEZONE` | `Asia/Seoul` | Your local timezone |

## MCP Tools

The server exposes 6 tools via MCP:

| Tool | Description |
|------|-------------|
| `list_events` | Query events by calendar and time range |
| `create_event` | Create a new event |
| `update_event` | Modify an existing event |
| `delete_event` | Delete an event |
| `list_calendars` | List all accessible calendars |
| `create_calendar` | Create a new calendar |
