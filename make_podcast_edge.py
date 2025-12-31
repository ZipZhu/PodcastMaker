import asyncio
import re
from pathlib import Path
import subprocess
from datetime import datetime
import edge_tts

# ====== 角色音色 ======
VOICE_A = "zh-CN-XiaoxiaoNeural"  # 女声
VOICE_B = "zh-CN-YunxiNeural"     # 男声（可换：zh-CN-YunjianNeural 更稳）

# ====== 语速/语调/音量（格式严格：必须带 + 或 -）======
RATE_A = "+10%"
PITCH_A = "+0Hz"
VOLUME_A = "+8%"

RATE_B = "+20%"
PITCH_B = "+2Hz"
VOLUME_B = "+5%"

# ====== 输入输出 ======
TEXT_FILE = "script.txt"
OUT_ROOT = "outputs"   # outputs/时间戳/...
TTS_TIMEOUT = 120

def parse_lines(text: str):
    items = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r'^\s*([ABab])\s*[：:]\s*(.+)$', line)
        if m:
            role = m.group(1).upper()
            utt = m.group(2).strip()
            if utt:
                items.append((role, utt))
        else:
            items.append(("B", line))
    return items

async def synth(text: str, role: str, out_path: Path):
    if role == "A":
        voice = VOICE_A
        rate, pitch, volume = RATE_A, PITCH_A, VOLUME_A
    else:
        voice = VOICE_B
        rate, pitch, volume = RATE_B, PITCH_B, VOLUME_B

    comm = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    await asyncio.wait_for(comm.save(str(out_path)), timeout=TTS_TIMEOUT)

def ensure_ffmpeg_available():
    subprocess.run(
        ["ffmpeg", "-version"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def merge_mp3(seg_dir: Path, out_mp3: Path):
    """
    在 seg_dir 下生成 list.txt，然后用 ffmpeg concat 合并输出到 out_mp3（绝对路径）
    """
    ensure_ffmpeg_available()

    files = sorted(seg_dir.glob("*.mp3"))
    if not files:
        raise RuntimeError(f"没有找到可合并的 mp3：{seg_dir}")

    list_file = seg_dir / "list.txt"
    list_file.write_text("\n".join([f"file '{f.name}'" for f in files]), encoding="utf-8")

    out_abs = str(out_mp3.resolve())

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", out_abs],
            check=True,
            cwd=str(seg_dir),
        )
    except subprocess.CalledProcessError:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt",
             "-c:a", "libmp3lame", "-qscale:a", "4", out_abs],
            check=True,
            cwd=str(seg_dir),
        )

async def main():
    base = Path.cwd()
    print("== Edge TTS 多角色对话生成开始 ==")
    print("工作目录：", base)

    p = Path(TEXT_FILE)
    if not p.exists():
        print(f"找不到 {TEXT_FILE}")
        return

    text = p.read_text(encoding="utf-8-sig").strip()
    if not text:
        print(f"{TEXT_FILE} 为空")
        return

    lines = parse_lines(text)
    print(f"共 {len(lines)} 句台词。")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = Path(OUT_ROOT) / run_id
    seg_dir = run_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)

    # 1) 保存本次输入文本到输出目录
    script_out = run_dir / f"script_{run_id}.txt"
    script_out.write_text(text + "\n", encoding="utf-8")

    # 2) 本次成品 mp3
    out_mp3 = run_dir / f"podcast_{run_id}.mp3"

    # 3) 分段生成
    for i, (role, utt) in enumerate(lines, 1):
        out_seg = seg_dir / f"{i:04d}_{role}.mp3"
        print(f"[{i}/{len(lines)}] {role} -> {run_id}\\segments\\{out_seg.name}")
        await synth(utt, role, out_seg)

    # 4) 合并
    print("开始自动合并…")
    merge_mp3(seg_dir, out_mp3)

    print("完成：", out_mp3.resolve())
    print("本次输出目录：", run_dir.resolve())

if __name__ == "__main__":
    asyncio.run(main())

