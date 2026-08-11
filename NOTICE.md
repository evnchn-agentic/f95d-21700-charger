# Attribution and terms

This is a **derivative work**. The original housing is:

> **共田F95D风扇外壳** — by **李李子**, published on MakerWorld.
> Stated terms in the author's own safety/licence document:
> *"本设计依据开源许可证（如 CERN-OHL-W v2、GPL-3.0 等）向您开放下载、修改与再发布权利，
> 本人仍依法享有该设计文件的完整著作权。"*
> — i.e. download, modify and **republish** are granted.

## A tension worth naming rather than papering over

The author names **CERN-OHL-W v2 / GPL-3.0**, both of which permit commercial use, and
*separately* reserves commercial rights: *"禁止商业售卖 … 未经本人书面授权，任何自然人、
法人或组织不得将本设计（含修改版本）及其衍生实物以营利为目的进行生产、销售、众筹、
有偿定制或其他形式的商业利用。"*

Those two statements do not fully agree. This repository therefore does **not** ship a clean
OSI `LICENSE` file that would misrepresent the upstream terms. Instead:

- Treat this as **share-alike, non-commercial** — the stricter reading, which respects the
  author's clearly stated intent.
- **Personal, non-commercial use only.** For anything commercial, contact the original author.
- If you republish a further derivative, carry this NOTICE forward and credit 李李子.

## What is and is not redistributed here

- **Redistributed:** the two remixed shells. They are derivative geometry — the donor's
  interior is preserved byte-for-byte in the electronics region by design, so they cannot
  meaningfully be separated from the original.
- **Not redistributed:** the donor's unmodified parts (battery door, button, light pipe,
  kickstand legs, magnetic mount, duct ring, nameplate, bearing tools). Get those from the
  original model — this remix only replaces two of its parts.

## Safety

A lithium cell in a printed enclosure. The upstream author's三原则 apply and are repeated here:
**disconnect power before working on it → run a no-load test → inspect periodically.**
Do not print in PLA.
