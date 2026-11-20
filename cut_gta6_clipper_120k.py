#!/usr/bin/env python3
"""Re-cut of moments.md #9 (120k viewers) for make.fun gta6-clipper-01,
replacing the end-stream entry video on the user's order 2026-11-20 ~15:45 WIB.

Moment: 120.000 viewer nonton ketampanan Windah, 26:35-27:15 (1595-1635s)
from windah-gta6-720p.mp4. User picked the already-published clip4
(https://youtube.com/shorts/K-rRlH_IX6o, 1,180 views, most-viewed after the
end-stream clip) as the new entry.
Rules for make.fun entries (user 2026-11-20): NO motionklip watermark strip,
NO motion klip end template. The video pitches make.fun only.
- Hook: big on-screen title for the first 5s, matching the caption:
  "120.000 VIEWER" / "NONTON KETAMPANAN WINDAH!".
- Subtitles: burned-in Anton, enlarged to 68 with a thicker outline (4)
  so they read clearly, max 20 chars per cue.
- make.fun pitch: after the moment, a 5s end card:
  "Make clips like this with AI and earn money on make.fun" +
  "make.fun/bounty/gta6-clipper-01". No end template after it.
- Layout: blurred-background vertical 720x1280, gameplay 720x405 centred,
  Windah facecam visible (bottom-right of source), no centre-crop.
"""
import json, os, re, subprocess, sys

WORK = os.path.expanduser("~/workspace/clips-gta6")
SRC = os.path.join(WORK, "windah-gta6-720p.mp4")
FONT_ANTON = os.path.expanduser("~/.fonts/Anton-Regular.ttf")
FONT_MONTS = os.path.expanduser("~/.fonts/Montserrat-ExtraBold-static.ttf")
OUT = os.path.join(WORK, "clip-makefun-gta6-120k.mp4")
ASS = os.path.join(WORK, "clip-makefun-gta6-120k.ass")

START, END = 1595, 1635  # 26:35 - 27:15, 40s
PITCH_DUR = 5

def parse_transcript():
    d = json.load(open(os.path.join(WORK, "transcript.json")))
    tr = json.loads(d["content"][0]["text"])["transcription"]
    lines = []
    for m in re.finditer(r"\[((\d+):)?(\d+):(\d+)\]\s*(.+?)(?=\n\[\d+(?::\d+){1,2}\]|\Z)", tr, re.S):
        hh = int(m.group(2)) if m.group(2) else 0
        lines.append((hh*3600 + int(m.group(3))*60 + int(m.group(4)),
                      m.group(5).replace("\n", " ").strip()))
    return lines

def split_text(txt, maxlen=20):
    words, chunks, cur = txt.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > maxlen and cur:
            chunks.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        chunks.append(cur)
    return chunks

def fmt_ass(t):
    cs = int(round((t - int(t)) * 100))
    if cs == 100:
        t, cs = int(t) + 1, 0
    return f"{int(t)//3600}:{int(t)//60%60:02d}:{int(t)%60:02d}.{cs:02d}"

def clean_txt(txt):
    txt = re.sub(r"\[[^\]]*\]", "", txt)
    txt = re.sub(r"^[A-Za-z]\s+", "", txt)
    return re.sub(r"\s+", " ", txt).strip()

def build_ass(lines, start, end, path):
    segs = [(t, clean_txt(x)) for t, x in lines if start - 2 <= t <= end]
    segs = [(t, x) for t, x in segs if x]
    out = ["[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\nScaledBorderAndShadow: yes\n",
           "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Anton,68,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,4,0,2,30,30,110,1\n",
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    n = 0
    for i, (t, txt) in enumerate(segs):
        t0 = max(t, start)
        t1 = segs[i+1][0] if i+1 < len(segs) else end
        t1 = min(t1, end)
        if t1 - t0 < 0.6:
            t1 = min(t0 + 1.2, end)
        chunks = split_text(txt)
        if not chunks:
            continue
        dur = (t1 - t0) / len(chunks)
        for j, ch in enumerate(chunks):
            a, b = t0 + j*dur, t0 + (j+1)*dur
            out.append(f"Dialogue: 0,{fmt_ass(a-start)},{fmt_ass(b-start)},Default,,0,0,0,,{ch}")
            n += 1
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    return n

def main():
    lines = parse_transcript()
    n = build_ass(lines, START, END, ASS)
    print(f"ASS cues: {n} -> {ASS}")

    # --- segment 0: the moment, vertical, clear subtitles, hook title ---
    hook = (
        f"drawtext=fontfile={FONT_MONTS}:text='120.000 VIEWER':fontsize=72:"
        f"fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=70:"
        f"enable='between(t,0,5)',"
        f"drawtext=fontfile={FONT_MONTS}:text='NONTON KETAMPANAN WINDAH!':fontsize=40:"
        f"fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=160:"
        f"enable='between(t,0,5)'"
    )
    moment_fc = (
        f"[0:v]split[a][b];"
        f"[a]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,gblur=sigma=30,eq=brightness=-0.08[bg];"
        f"[b]scale=720:405,setsar=1,fps=30,format=yuv420p[fg];"
        f"[bg][fg]overlay=(W-w)/2:437,setsar=1,format=yuv420p,"
        f"subtitles='{ASS}',{hook},"
        f"format=yuv420p[v0];"
        f"[0:a]aresample=48000[a0]"
    )
    # --- segment 1: make.fun pitch card, 5s, silent ---
    pitch_fc = (
        f"color=c=black:s=720x1280:d={PITCH_DUR}:r=30,format=yuv420p,"
        f"drawtext=fontfile={FONT_MONTS}:text='MAKE CLIPS LIKE THIS':fontsize=52:"
        f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=430,"
        f"drawtext=fontfile={FONT_MONTS}:text='WITH AI':fontsize=52:"
        f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=500,"
        f"drawtext=fontfile={FONT_MONTS}:text='AND EARN MONEY ON':fontsize=44:"
        f"fontcolor=yellow:borderw=2:bordercolor=black:x=(w-text_w)/2:y=590,"
        f"drawtext=fontfile={FONT_MONTS}:text='make.fun':fontsize=110:"
        f"fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=660,"
        f"drawtext=fontfile={FONT_MONTS}:text='make.fun/bounty/gta6-clipper-01':fontsize=30:"
        f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=830,"
        f"setsar=1[v1];"
        f"anullsrc=r=48000:cl=stereo,atrim=0:{PITCH_DUR},asetpts=PTS-STARTPTS[a1]"
    )
    fc = moment_fc + ";" + pitch_fc + ";" + \
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"

    cmd = ["ffmpeg", "-y", "-v", "error",
           "-ss", str(START), "-to", str(END), "-i", SRC,
           "-filter_complex", fc,
           "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT]
    print("rendering", OUT, "...")
    r = subprocess.run(cmd)
    print("ffmpeg rc:", r.returncode)
    if r.returncode == 0:
        print("size:", os.path.getsize(OUT))

if __name__ == "__main__":
    main()
