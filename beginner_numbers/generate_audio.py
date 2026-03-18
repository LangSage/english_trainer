#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import time

from gtts import gTTS

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / 'audio'
MANIFEST_PATH = ROOT / 'manifest.js'
LANG = 'en'
SLOW = False

ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
TEENS = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']


def number_to_words(n: int) -> str:
    if n < 10:
        return ONES[n]
    if n < 20:
        return TEENS[n - 10]
    if n < 100:
        tens, rest = divmod(n, 10)
        return TENS[tens] if rest == 0 else f'{TENS[tens]}-{ONES[rest]}'
    if n == 100:
        return 'one hundred'
    raise ValueError(f'Only 1..100 supported, got: {n}')


def build_manifest() -> list[dict]:
    data = []
    for n in range(1, 101):
        data.append({
            'number': n,
            'text': number_to_words(n),
            'file': f'audio/n_{n}.mp3'
        })
    return data


def write_manifest_js(manifest: list[dict]) -> None:
    js = '// Auto-generated manifest for the Numbers Trainer\n'
    js += 'window.MANIFEST = '
    js += json.dumps(manifest, ensure_ascii=False, indent=2)
    js += ';\n'
    MANIFEST_PATH.write_text(js, encoding='utf-8')
    print(f'✓ wrote {MANIFEST_PATH.name}')


def synthesize_one(number: int, overwrite: bool = False) -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    target = AUDIO_DIR / f'n_{number}.mp3'
    text = number_to_words(number)

    if target.exists() and not overwrite:
        print(f'✓ exists: {target.name}')
        return

    print(f'- generating: {target.name}  ->  "{text}"')
    tts = gTTS(text=text, lang=LANG, slow=SLOW)
    tts.save(str(target))
    time.sleep(0.1)


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate English audio files for numbers 1 to 100.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing mp3 files.')
    parser.add_argument('--start', type=int, default=1, help='Start number, default 1.')
    parser.add_argument('--end', type=int, default=100, help='End number, default 100.')
    args = parser.parse_args()

    start = max(1, args.start)
    end = min(100, args.end)
    if start > end:
        raise SystemExit('Start must be less than or equal to end.')

    manifest = build_manifest()
    write_manifest_js(manifest)

    for n in range(start, end + 1):
        synthesize_one(n, overwrite=args.overwrite)

    print('Done.')
    print('Upload the whole folder to GitHub Pages after generation.')


if __name__ == '__main__':
    main()
