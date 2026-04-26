#!/usr/bin/env python3

import sys
from pathlib import Path

import av
from cueparser import CueSheet
from mutagen.flac import FLAC
from pathvalidate import sanitize_filename


def extract_metadata(flac: FLAC) -> dict:
    meta = {}

    for key, values in flac.items():
        if key.lower() == "cuesheet":
            continue
        if not values:
            continue
        meta[key.lower()] = values[0]

    return meta


def track_metadata(base_meta: dict, track_num: int, title: str) -> dict:
    meta = base_meta.copy()
    meta["tracknumber"] = str(track_num)
    meta["title"] = title
    return meta


def cue_time_to_seconds(t: str) -> float:
    m, s, f = map(int, t.split(":"))
    return m * 60 + s + f / 75.0


def parse_cue(cue_text: str | None) -> CueSheet:
    if not cue_text:
        msg = "No embedded CUESHEET found in FLAC metadata"
        raise RuntimeError(msg)

    cue = CueSheet()
    cue.setOutputFormat("%performer% - %title%", "%performer% - %title% %index%")
    cue.setData(cue_text)
    cue.parse()

    return cue


def parse_cue_tracks(cue_tracks: list) -> list[dict]:
    tracks = []

    for t in cue_tracks:
        offset = getattr(t, "offset", None)
        if offset is None:
            continue

        tracks.append(
            {
                "number": int(getattr(t, "number", 0)),
                "title": getattr(t, "title", "Unknown"),
                "offset": cue_time_to_seconds(offset),
            },
        )

    if not tracks:
        msg = "cueparser produced no usable tracks"
        raise RuntimeError(msg)

    return tracks


def main(path: Path) -> None:
    flac = FLAC(str(path))

    artist = flac.get("albumartist", flac.get("artist", ["Unknown"]))[0]
    album = flac.get("album", ["Unknown Album"])[0]
    date = flac.get("date", ["0000"])[0][:4]

    cue = parse_cue(flac.get("cuesheet", [None])[0])
    tracks = parse_cue_tracks(cue.tracks)

    base_meta = extract_metadata(flac)

    container = av.open(str(path))
    audio_stream = next(s for s in container.streams if s.type == "audio")

    outdir = Path(sanitize_filename(artist)) / f"{date} - {sanitize_filename(album)}"
    outdir.mkdir(parents=True, exist_ok=True)

    for i, track in enumerate(tracks):
        start = track["offset"]
        end = tracks[i + 1]["offset"] if i + 1 < len(tracks) else None

        num = str(track["number"]).zfill(2)
        title = sanitize_filename(track["title"])

        outfile = outdir / f"{num} - {title}.ogg"

        container.seek(int(start / audio_stream.time_base), stream=audio_stream)

        output = av.open(str(outfile), "w")
        out_stream = output.add_stream("libvorbis", rate=audio_stream.rate)
        out_stream.codec_context.options["q"] = "6"

        metadata = track_metadata(base_meta, track["number"], track["title"])
        out_stream.metadata.update(metadata)

        for packet in container.demux(audio_stream):
            for frame in packet.decode():
                if frame.pts is None:
                    continue

                t = frame.pts * frame.time_base

                if end is not None and t > end:
                    break

                pkt = out_stream.encode(frame)
                if pkt:
                    output.mux(pkt)

        for pkt in out_stream.encode():
            output.mux(pkt)

        output.close()

        print(f"Created: {outfile}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: splitflac.py file.flac")
        sys.exit(1)

    main(Path(sys.argv[1]))
