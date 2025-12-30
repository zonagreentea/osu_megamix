# osu_megamix

A **free and open** rhythm game inspired by osu!, written in Python and C++.
Anyone can contribute, fork, or modify — no license restrictions.

## Features

- Fully playable rhythm game
- Python version with simple UI
- C++ engine version for performance
- Persistent logging for game sessions
- Continuous build/run scripts supported

## Setup

### Python Version
Run the Python version directly:
```bash
python3 osu_megamix.py
```

### C++ Version
Build the C++ engine:
```bash
cd ~/release/osu-megamix/osu_megamix_src
g++ -std=c++17 -O2 *.cpp -o osu_megamix
```

## Running

Run in a loop with logs:
```bash
mkdir -p ~/osu_megamix_build_log
nohup bash -c 'while true; do ./osu_megamix >> ~/osu_megamix_build_log/full_send.log 2>&1; sleep 1; done' &
```

## Contributing

- Fork the repository
- Create a new branch
- Make changes and submit a Pull Request

No license restrictions — everyone is welcome to contribute, modify, and share.
