#!/usr/bin/env bash

# time is authoritative
timeline=0

while true; do
    input="$(read_input)"

    # event enters the timeline
    event="$(receive_event "$input")"

    # player interacts with the event
    interaction="$(player_interaction "$event")"

    # event + interaction produce output
    output="$(process_event "$event" "$interaction")"

    emit_output "$output"

    # timeline slides forward
    timeline=$((timeline + 1))
done