# Notes

## Later
- Gmail + Google Calendar, read-only (`gmail.readonly`, `calendar.readonly`). Desktop OAuth client, token stored locally, mail only ever goes to the local model. No send/delete scopes.
- Custom wake word "hey clanker" (openWakeWord training run).
- AEC reference from WASAPI loopback of the whole output, so barge-in works over music.
- Optional: mute Discord mic while the assistant listens (would need its keybind).

## Benchmarks (2026-11-10, Ollama 0.30.10, ROCm, RX 9060 XT)
| Model | VRAM | Cold load | TTFT warm | Decode | Tool call |
|---|---|---|---|---|---|
| qwen3.5:9b | 5.2 GB, all GPU | 7.2 s | 0.25 s | 46 tok/s | 1.2 s, correct |
| qwen3.5:9b with VRAM full (Fusion + Explorer leak) | paged out | 11 s | 0.3 s | 11 tok/s | 4.1 s |
| qwen3.5:35b (MoE, 3B active) | 14.8 of 34 GB, rest in RAM | 36 s | 0.3 s | 23 tok/s | 6.3 s, correct |

35b took system RAM to 0.1 GB free with Fusion closed. Not viable.
