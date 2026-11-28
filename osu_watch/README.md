# osu!watch 1 — broadcast prototype

A dependency-free, continuously advancing local TV channel with a shared UTC schedule, live program guide, procedural station visuals, and reserved sponsor support. The clock progresses even while the server is stopped; when restarted, the current slot is calculated from UTC time. No actual media streaming or gameplay capture is implemented yet.

## Run

```sh
cd osu_watch
python3 -m unittest -v test_channel.py
python3 channel.py
```

Open http://127.0.0.1:8765 in a browser. Stop with Ctrl+C. Use `--host 0.0.0.0` only on a trusted network after reviewing access controls.

## Integrate

Copy the `osu_watch` folder into the root of `osu_megamix` and launch it separately. Add a menu link to `http://127.0.0.1:8765` once the main menu's entry points are confirmed. No existing game files are modified.

## Programming

Edit `schedule.json`. Each entry needs `id`, `kind`, `title`, `subtitle`, `duration_seconds` (positive integer). Sponsor segments must have `kind: "sponsor"` and `approved: true`, and must be labeled sponsored on screen. Restart server after edits. Do not include unlicensed music, gameplay, or promotional assets.

This is a broadcast scheduler and placeholder visuals, not yet a 24/7 video encoder or live gameplay feed.

## Live studio

Open `http://127.0.0.1:8765/studio`, prepare the studio, choose a camera or screen source, and go live. Enable **Include system audio** before sharing a screen or tab; in the browser permission prompt, select **Share audio**. The selected screen video and system audio are mixed with the microphone and sent to viewers through the existing WebRTC broadcast path. Browser and operating-system support for system-audio capture varies, so the studio reports when only screen video was received.
