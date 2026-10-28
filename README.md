# GeigerLog (HomeKit Fork)

This is a fork of [ullix/GeigerLog](https://github.com/ullix/GeigerLog) specifically modified to bridge a GMC-300S Geiger counter to Apple HomeKit via Homebridge.

It adds a background thread to the serial fetching process that pushes the latest CPM (Counts Per Minute) reading to a GitHub Gist. A separate Homebridge instance on your local network polls that Gist and exposes it to the Apple Home app as a Light Sensor (which allows displaying raw integer values).

For the original software documentation, see the SourceForge page linked in the upstream repository.

## Architecture

1. GeigerLog (macOS/Linux): Connects to the GMC-300S, filters hardware overflow spikes (32768), and pushes the clean data to a GitHub Gist every 60 seconds.
2. GitHub Gist: Acts as a public/private bridge between your machine and your Homebridge server (useful if they are on different networks).
3. Homebridge (Docker/Linux): Uses the homebridge-cmd4 plugin to fetch the Gist URL every 60 seconds and update a HomeKit accessory.

## Setup Instructions

### 1. GeigerLog Configuration

Apply a custom.cfg in the gconfig/ directory to enforce a 5-second logging cycle and disable CPS (which causes serial buffer desyncs on the 300S):

[Logging]
LogCycle = 5

[MonServer]
MonServerAutostart = no

[GMC_Device]
GMC_Activation = yes
GMC_Variables = CPM1st, -

[ValueFormula]
CPM1st = val
CPS1st = val

### 2. Create the GitHub Gist

The bridge uses a GitHub Gist as a relay. The Mac writes to it, and Homebridge reads from it.

1. Go to https://gist.github.com
2. Create a new Secret Gist with the filename geiger.txt and the content 0.
3. Save the Gist. Look at the URL in your browser; it will look like:
   https://gist.github.com/YOUR_USERNAME/a664e87ad6db06cc1eedd8f3c7ef15a3
4. Note the Gist ID (the long alphanumeric string at the end) and your GitHub Username. You will need both.

### 3. Create the GitHub Token

The background push script needs permission to update the Gist.

1. Go to https://github.com/settings/tokens (GitHub Settings > Developer Settings > Tokens classic)
2. Click Generate new token (classic).
3. Give it a name (e.g., GeigerLog-Homebridge) and set an expiration.
4. Under Select scopes, check the box for gist. (Do not check anything else).
5. Click Generate token and copy the resulting ghp_... string.

Add the token to your shell profile (~/.zshrc or ~/.bashrc):

export GITHUB_GEIGER_GIST_TOKEN="ghp_yourTokenHere"

Reload your shell:

source ~/.zshrc

### 4. Configure the Push Script

Open scripts/push_to_gist.py and update the GIST_ID line to match the Gist you created in Step 2:

GIST_ID = "a664e87ad6db06cc1eedd8f3c7ef15a3"  # Replace with your Gist ID

Note on GitHub Rate Limits: The Gist API has a strict limit of 100 updates per hour. The background thread in gdev_gmc.py is rate-limited to push only every 12th logging cycle (12 * 5s = 60 seconds), which equals 60 pushes per hour.

### 5. Homebridge Configuration

You must have the homebridge-cmd4 plugin installed on your Homebridge server (https://github.com/ztalbot2000/homebridge-cmd4).

Because Homebridge often runs in a stripped-down Docker container, we use python3 (which is pre-installed in the standard Homebridge image) instead of curl to fetch the Gist. This avoids shell parsing issues and missing binaries.

Add the following to your Homebridge config.json under the "platforms" array:

{
    "platform": "Cmd4",
    "name": "Cmd4",
    "accessories": [
        {
            "type": "LightSensor",
            "displayName": "Geiger Counter",
            "name": "Geiger Counter",
            "polling": true,
            "interval": 60,
            "state_cmd": "/usr/bin/env python3 -c \"import urllib.request; print(urllib.request.urlopen('https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/geiger.txt').read().decode().strip())\""
        }
    ]
}

Note: Replace YOUR_USERNAME and YOUR_GIST_ID with your actual GitHub details.

Restart Homebridge. The Geiger Counter accessory should appear in your Apple Home app. It will be categorized as a Light Sensor (and may show "Dark" in the UI), but the integer displayed is your current CPM.

## Modifications to Core Code

- gdev_gmc.py:
  - Added a threading block inside THREAD_GMC_fetchValues to trigger the Gist push asynchronously so it doesn't block the serial port.
  - Added a filter in fetchSingleValueGMC to catch the GMC-300S 32768 overflow spikes (if value >= 20000: value = g.NAN) and prevent them from ever reaching the database or the plot.
