#!/usr/bin/env python3
"""
城市扩张历史动态 (Timelapse)
使用 Landsat 数据生成城市扩张延时摄影
"""

import ee
import geemap
import os
import sys
from datetime import datetime

def create_city_timelapse(
    city_name: str,
    start_year: int = 1984,
    end_year: int = None,
    output_dir: str = "."
) -> dict:
    """
    生成城市扩张历史延时摄影 GIF

    Args:
        city_name: 城市名称 (如 "Beijing", "Las Vegas")
        start_year: 起始年份 (Landsat 数据从 1984 年开始)
        end_year: 结束年份，默认为当前年份
        output_dir: 输出目录

    Returns:
        dict: 包含 gif_path 和元数据的结果字典
    """
    # 初始化 Earth Engine
    PROJECT_ID = "project-37ebd001-5648-4239-916"
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)

    if end_year is None:
        end_year = datetime.now().year

    # 验证年份范围
    if start_year < 1984:
        print("警告: Landsat 数据从 1984 年开始，已自动调整起始年份")
        start_year = 1984

    # 获取城市边界
    print(f"正在获取 {city_name} 的边界...")
    city_boundary = geemap.osm_to_ee(city_name, which_result=1)

    # 生成 GIF 文件名
    gif_filename = f"{city_name.replace(' ', '_')}_timelapse_{start_year}_{end_year}.gif"
    gif_path = os.path.join(output_dir, gif_filename)

    print(f"正在生成 {start_year}-{end_year} 年延时摄影...")
    print("(这可能需要几分钟时间...)")

    # 调用 geemap 的 landsat_timelapse 函数
    result_path = geemap.landsat_timelapse(
        roi=city_boundary,
        out_gif=gif_path,
        start_year=start_year,
        end_year=end_year,
        start_date="06-10",  # 夏季数据
        end_date="09-20",
        bands=["NIR", "Red", "Green"],  # 假彩色合成，更易辨别城市扩张
        apply_fmask=True,  # 云掩膜
        dimensions=768,
        frames_per_second=3,
        title=f"{city_name} Urban Expansion ({start_year}-{end_year})",
        title_xy=("2%", "90%"),
        add_text=True,
        text_xy=("2%", "2%"),
        font_size=20,
        font_color="white",
        add_progress_bar=True,
        progress_bar_color="white",
        progress_bar_height=5,
        loop=0  # 无限循环
    )

    print(f"延时摄影已保存至: {gif_path}")

    result = {
        "city": city_name,
        "start_year": start_year,
        "end_year": end_year,
        "duration_years": end_year - start_year,
        "gif_path": gif_path,
        "analysis_tips": [
            "观察城市边缘的变化，识别主要扩张方向",
            "亮色区域通常代表城市建成区",
            "绿色区域代表植被/农田",
            "注意河流、湖泊等自然边界对扩张的影响"
        ]
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python city_timelapse.py <城市名称> [起始年份] [结束年份] [输出目录]")
        print("示例: python city_timelapse.py 'Las Vegas' 1984 2024 ./output")
        sys.exit(1)

    city_name = sys.argv[1]
    start_year = int(sys.argv[2]) if len(sys.argv) > 2 else 1984
    end_year = int(sys.argv[3]) if len(sys.argv) > 3 else None
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "."

    os.makedirs(output_dir, exist_ok=True)

    result = create_city_timelapse(city_name, start_year, end_year, output_dir)

    print("\n" + "=" * 50)
    print(f"城市扩张延时摄影 - {result['city']}")
    print("=" * 50)
    print(f"时间跨度: {result['start_year']} - {result['end_year']} ({result['duration_years']} 年)")
    print(f"GIF 文件: {result['gif_path']}")
    print("\n解读建议:")
    for tip in result['analysis_tips']:
        print(f"  - {tip}")
    print("=" * 50)


if __name__ == "__main__":
    main()
