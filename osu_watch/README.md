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

## Microphone studio

Open http://127.0.0.1:8765 and click **Enable microphone**. Grant browser permission. The level meter previews local audio. Optionally check **Hear myself** with headphones to avoid feedback. **Disconnect** releases the microphone. This version does not transmit, record, or inject microphone audio into the public broadcast. Live transmission requires an authenticated broadcaster-to-server audio pipeline and viewer audio playback.
