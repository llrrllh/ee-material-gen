#!/usr/bin/env python3
"""Extract dominant colors from course brochure PDFs."""

import json
from collections import Counter

from settings import get_settings

settings = get_settings()
BROCHURE_DIR = settings.brochure_dir
OUTPUT_FILE = settings.courses_colors_output_file

COURSES = [
    {
        "id": "EE-QYJ",
        "course_name": "企业家战略思维与创新管理课程",
        "files": [
            "【课程手册】企业家战略思维与创新管理课程【最新版】.jpg",  # JPG fallback
            "【课程手册】企业家战略思维与创新管理课程【2025版】.pdf",
        ],
    },
    {
        "id": "EE-CMO",
        "course_name": "首席营销官课程",
        "files": ["【课程手册】首席营销官课程【最新版简章】.pdf"],
    },
    {
        "id": "EE-CFO",
        "course_name": "首席财务官课程",
        "files": ["【课程手册】首席财务官课程【最新版简章】.pdf"],
    },
    {
        "id": "EE-GMP",
        "course_name": "高级经理工商管理核心课程",
        "files": ["【课程手册】高级经理工商管理核心课程【最新版】.pdf"],
    },
    {
        "id": "EE-SCM",
        "course_name": "全球供应链管理课程",
        "files": [
            "【课程手册】全球供应链管理课程【2025版】.pdf",
            "【课程手册】全球供应链管理课程【最新版】.docx",
        ],
    },
    {
        "id": "EE-FCA",
        "course_name": "非财务高管的财务管理课程",
        "files": ["【课程手册】非财务高管的财务管理课程【最新版简章】.pdf"],
    },
    {
        "id": "EE-MA",
        "course_name": "资本运作与并购重组",
        "files": ["【课程手册】资本运作与并购重组【最新版简章】.pdf"],
    },
    {
        "id": "EE-AI2",
        "course_name": "人工智能领创计划（二期）",
        "files": ["【课程手册】人工智能领创计划（二期）【最新版】.pdf"],
    },
    {
        "id": "EE-AIH",
        "course_name": "人工智能领航计划",
        "files": ["【课程手册】人工智能领航计划【2025版】.pdf"],
    },
    {
        "id": "EE-DH",
        "course_name": "生命健康产业领航计划",
        "files": ["【课程手册】生命健康产业领航计划【2025版】.pdf"],
    },
    {
        "id": "EE-PEMBA",
        "course_name": "后EMBA课程",
        "files": ["【课程手册】后EMBA课程【最新版】.pdf"],
    },
    {
        "id": "EE-HFP",
        "course_name": "中国哲学与时代精神项目",
        "files": ["【课程手册】中国哲学与时代精神项目【最新版】.pdf"],
    },
]


def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(int(r), int(g), int(b))


def is_near_white(r, g, b, threshold=230):
    return r > threshold and g > threshold and b > threshold


def is_near_black(r, g, b, threshold=30):
    return r < threshold and g < threshold and b < threshold


def is_near_gray(r, g, b, sat_threshold=20):
    """Check if color is near gray (low saturation)."""
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    return (max_c - min_c) < sat_threshold


def color_distance(c1, c2):
    """Simple euclidean distance in RGB space."""
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5


def cluster_colors(colors, threshold=30):
    """Group similar colors together, return list of (representative, count)."""
    clusters = []
    for color, count in colors:
        found = False
        for cluster in clusters:
            if color_distance(color, cluster[0]) < threshold:
                cluster[1] += count
                found = True
                break
        if not found:
            clusters.append([color, count])
    clusters.sort(key=lambda x: -x[1])
    return clusters


def extract_colors_from_pdf(pdf_path, max_pages=2, sample_step=4):
    """Extract dominant colors from first pages of a PDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None, "PyMuPDF (fitz) not installed"

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        return None, f"Cannot open PDF: {e}"

    all_colors = []
    dark_colors = []
    pages_analyzed = min(max_pages, len(doc))

    for page_num in range(pages_analyzed):
        page = doc[page_num]
        # Render at lower resolution for speed
        mat = fitz.Matrix(0.5, 0.5)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)

        # Sample pixels
        samples = pix.samples
        width, height = pix.width, pix.height

        for y in range(0, height, sample_step):
            for x in range(0, width, sample_step):
                idx = (y * width + x) * 3
                if idx + 2 < len(samples):
                    r, g, b = samples[idx], samples[idx + 1], samples[idx + 2]
                    # Skip near-white, near-black, near-gray for main palette
                    if not is_near_white(r, g, b) and not is_near_black(r, g, b) and not is_near_gray(r, g, b):
                        # Quantize to reduce unique colors
                        qr = (r // 16) * 16
                        qg = (g // 16) * 16
                        qb = (b // 16) * 16
                        all_colors.append((qr, qg, qb))
                    # Collect dark background candidate colors from page 0
                    if page_num == 0 and 5 <= r <= 80 and 5 <= g <= 80 and 5 <= b <= 80:
                        dark_colors.append(((r // 8) * 8, (g // 8) * 8, (b // 8) * 8))

    doc.close()

    if not all_colors:
        return None, "No significant colors found (page may be mostly B&W)"

    # Count and cluster
    color_counts = Counter(all_colors).most_common(50)
    clusters = cluster_colors(color_counts, threshold=40)

    if not clusters:
        return None, "No clusters found"

    primary = rgb_to_hex(*clusters[0][0])
    secondary = rgb_to_hex(*clusters[1][0]) if len(clusters) > 1 else primary
    tertiary = rgb_to_hex(*clusters[2][0]) if len(clusters) > 2 else secondary

    # Identify dark background from colors collected in main pass
    bg_dark = None
    if dark_colors:
        most_common_dark = Counter(dark_colors).most_common(1)[0][0]
        bg_dark = rgb_to_hex(*most_common_dark)

    return {
        "primary_color": primary,
        "accent_color": secondary,
        "tertiary_color": tertiary,
        "bg_dark": bg_dark or "#051024",
        "bg_light": "#F8F9FA",
        "text_on_dark": "#FFFFFF",
        "top_clusters": [rgb_to_hex(*c[0]) for c in clusters[:6]],
    }, None


def extract_colors_from_image(img_path, sample_step=4):
    """Extract dominant colors from an image file."""
    try:
        from PIL import Image
        img = Image.open(str(img_path)).convert("RGB")
        width, height = img.size
        all_colors = []
        for y in range(0, height, sample_step):
            for x in range(0, width, sample_step):
                r, g, b = img.getpixel((x, y))
                if not is_near_white(r, g, b) and not is_near_black(r, g, b) and not is_near_gray(r, g, b):
                    qr = (r // 16) * 16
                    qg = (g // 16) * 16
                    qb = (b // 16) * 16
                    all_colors.append((qr, qg, qb))

        if not all_colors:
            return None, "No significant colors found"

        color_counts = Counter(all_colors).most_common(50)
        clusters = cluster_colors(color_counts, threshold=40)
        primary = rgb_to_hex(*clusters[0][0]) if len(clusters) > 0 else "#000000"
        secondary = rgb_to_hex(*clusters[1][0]) if len(clusters) > 1 else primary
        tertiary = rgb_to_hex(*clusters[2][0]) if len(clusters) > 2 else secondary

        return {
            "primary_color": primary,
            "accent_color": secondary,
            "tertiary_color": tertiary,
            "bg_dark": "#051024",
            "bg_light": "#F8F9FA",
            "text_on_dark": "#FFFFFF",
            "top_clusters": [rgb_to_hex(*c[0]) for c in clusters[:6]],
        }, None
    except ImportError:
        return None, "Pillow not installed"
    except Exception as e:
        return None, str(e)


def main():
    results = {}

    for course in COURSES:
        course_id = course["id"]
        course_name = course["course_name"]
        print(f"\n--- Processing {course_id}: {course_name} ---")

        extracted = False
        for fname in course["files"]:
            fpath = BROCHURE_DIR / fname
            if not fpath.exists():
                print(f"  File not found: {fname}")
                continue

            print(f"  Using file: {fname}")
            suffix = fpath.suffix.lower()

            if suffix == ".pdf":
                colors, err = extract_colors_from_pdf(fpath)
                if err:
                    print(f"  Error: {err}")
                    continue
            elif suffix in (".jpg", ".jpeg", ".png"):
                colors, err = extract_colors_from_image(fpath)
                if err:
                    print(f"  Error: {err}")
                    continue
            else:
                print(f"  Skipping non-PDF/image: {fname}")
                continue

            if colors:
                print(f"  Primary: {colors['primary_color']}, Accent: {colors['accent_color']}")
                print(f"  Top colors: {colors.get('top_clusters', [])}")
                results[course_id] = {
                    "course_name": course_name,
                    "primary_color": colors["primary_color"],
                    "accent_color": colors["accent_color"],
                    "bg_dark": colors["bg_dark"],
                    "bg_light": colors["bg_light"],
                    "text_on_dark": colors["text_on_dark"],
                    "source_file": fname,
                    "extraction_note": "从封面像素分析提取",
                    "top_colors": colors.get("top_clusters", []),
                }
                extracted = True
                break

        if not extracted:
            print(f"  FAILED to extract colors for {course_id}")
            results[course_id] = {
                "course_name": course_name,
                "primary_color": "#00349A",
                "accent_color": "#D4AF37",
                "bg_dark": "#051024",
                "bg_light": "#F8F9FA",
                "text_on_dark": "#FFFFFF",
                "source_file": "",
                "extraction_note": "提取失败，使用默认配色",
                "top_colors": [],
            }

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Results saved to {OUTPUT_FILE}")
    return results


if __name__ == "__main__":
    results = main()
    print("\n=== SUMMARY ===")
    for cid, data in results.items():
        print(f"{cid}: primary={data['primary_color']} accent={data['accent_color']} note={data['extraction_note']}")
