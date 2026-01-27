#!/usr/bin/env python3
"""
水域面积变化监测 (NDWI 分析)
使用 Sentinel-2 数据监测城市水体面积变化
"""

import ee
import geemap
import os
import sys
from datetime import datetime

def analyze_water_change(
    city_name: str,
    year1: int,
    year2: int,
    output_dir: str = "."
) -> dict:
    """
    监测城市水域面积变化

    Args:
        city_name: 城市名称
        year1: 基准年份 (较早)
        year2: 对比年份 (较晚)
        output_dir: 输出目录

    Returns:
        dict: 包含水域变化百分比和对比图路径的结果字典
    """
    # 初始化 Earth Engine
    PROJECT_ID = "project-37ebd001-5648-4239-916"
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)

    # 验证年份
    if year1 < 2015:
        print("警告: Sentinel-2 数据从 2015 年开始，已自动调整年份")
        year1 = 2015
    if year2 < year1:
        year1, year2 = year2, year1

    # 获取城市边界
    print(f"正在获取 {city_name} 的边界...")
    city_boundary = geemap.osm_to_ee(city_name, which_result=1)

    def get_water_mask(year):
        """获取指定年份的水体掩膜"""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # 加载 Sentinel-2 数据
        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(city_boundary) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))

        # 云掩膜
        def mask_clouds(image):
            qa = image.select("QA60")
            cloud_bit_mask = 1 << 10
            cirrus_bit_mask = 1 << 11
            mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
                qa.bitwiseAnd(cirrus_bit_mask).eq(0)
            )
            return image.updateMask(mask).divide(10000)

        s2_masked = s2.map(mask_clouds)
        composite = s2_masked.median().clip(city_boundary)

        # 计算 MNDWI (Modified NDWI 更适合城市水体检测)
        # MNDWI = (Green - SWIR1) / (Green + SWIR1)
        # Sentinel-2: B3 = Green, B11 = SWIR1
        mndwi = composite.normalizedDifference(["B3", "B11"]).rename("MNDWI")

        # 水体阈值 (MNDWI > 0 通常表示水体)
        water_mask = mndwi.gt(0).rename("water")

        return mndwi, water_mask

    # 获取两个年份的水体数据
    print(f"正在分析 {year1} 年水体...")
    mndwi1, water1 = get_water_mask(year1)

    print(f"正在分析 {year2} 年水体...")
    mndwi2, water2 = get_water_mask(year2)

    # 计算水域像素数量
    print("正在计算水域面积变化...")

    def count_water_pixels(water_mask):
        stats = water_mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=city_boundary,
            scale=10,
            maxPixels=1e9
        )
        return stats.get("water").getInfo()

    water_pixels_1 = count_water_pixels(water1)
    water_pixels_2 = count_water_pixels(water2)

    # 计算变化百分比
    if water_pixels_1 > 0:
        change_percent = ((water_pixels_2 - water_pixels_1) / water_pixels_1) * 100
    else:
        change_percent = 100 if water_pixels_2 > 0 else 0

    # 生成评价
    if change_percent > 10:
        trend = "显著增加"
        trend_desc = "水域面积明显扩大，可能是新建水库、湿地恢复或降水增加"
    elif change_percent > 0:
        trend = "略有增加"
        trend_desc = "水域面积小幅增加"
    elif change_percent > -10:
        trend = "基本稳定"
        trend_desc = "水域面积变化不大"
    elif change_percent > -30:
        trend = "有所减少"
        trend_desc = "水域面积下降，需关注水资源保护"
    else:
        trend = "显著减少"
        trend_desc = "水域面积大幅缩减，建议重点关注"

    # 创建对比地图
    print("正在生成水体对比图...")
    Map = geemap.Map()
    Map.centerObject(city_boundary, 11)

    # MNDWI 可视化参数 (蓝色突出水体)
    mndwi_vis = {
        "min": -0.5,
        "max": 0.8,
        "palette": [
            "#8b4513",  # 棕色 - 陆地
            "#daa520",  # 金色
            "#f0e68c",  # 卡其色
            "#87ceeb",  # 天蓝色
            "#4169e1",  # 皇家蓝
            "#00008b"   # 深蓝 - 水体
        ]
    }

    # 水体变化可视化
    # 红色 = 水体减少，蓝色 = 水体增加，白色 = 无变化
    water_change = water2.subtract(water1).rename("change")
    change_vis = {
        "min": -1,
        "max": 1,
        "palette": ["#ff0000", "#ffffff", "#0000ff"]  # 红-白-蓝
    }

    Map.addLayer(mndwi1, mndwi_vis, f"{city_name} MNDWI {year1}")
    Map.addLayer(mndwi2, mndwi_vis, f"{city_name} MNDWI {year2}")
    Map.addLayer(water_change, change_vis, "水域变化 (红减蓝增)")
    Map.addLayer(city_boundary, {"color": "black"}, "City Boundary", False)

    # 添加图例
    Map.add_colorbar(
        change_vis,
        label="水域变化",
        layer_name="水域变化 (红减蓝增)"
    )

    # 保存地图
    map_filename = f"{city_name.replace(' ', '_')}_water_change_{year1}_{year2}.html"
    map_path = os.path.join(output_dir, map_filename)
    Map.to_html(map_path)
    print(f"对比图已保存至: {map_path}")

    # 估算面积 (每像素 10m x 10m = 100 平方米)
    pixel_area_sqkm = 100 / 1e6  # 平方公里
    area1_sqkm = water_pixels_1 * pixel_area_sqkm
    area2_sqkm = water_pixels_2 * pixel_area_sqkm

    result = {
        "city": city_name,
        "year1": year1,
        "year2": year2,
        "water_area_year1_sqkm": round(area1_sqkm, 2),
        "water_area_year2_sqkm": round(area2_sqkm, 2),
        "change_percent": round(change_percent, 2),
        "trend": trend,
        "trend_description": trend_desc,
        "map_path": map_path
    }

    return result


def main():
    if len(sys.argv) < 4:
        print("用法: python water_area_change.py <城市名称> <基准年份> <对比年份> [输出目录]")
        print("示例: python water_area_change.py Beijing 2016 2023 ./output")
        sys.exit(1)

    city_name = sys.argv[1]
    year1 = int(sys.argv[2])
    year2 = int(sys.argv[3])
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "."

    os.makedirs(output_dir, exist_ok=True)

    result = analyze_water_change(city_name, year1, year2, output_dir)

    print("\n" + "=" * 50)
    print(f"水域面积变化监测报告 - {result['city']}")
    print("=" * 50)
    print(f"基准年份: {result['year1']} (水域面积: {result['water_area_year1_sqkm']} km²)")
    print(f"对比年份: {result['year2']} (水域面积: {result['water_area_year2_sqkm']} km²)")
    print(f"变化百分比: {result['change_percent']:+.2f}%")
    print(f"变化趋势: {result['trend']}")
    print(f"分析: {result['trend_description']}")
    print(f"对比图文件: {result['map_path']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
