#!/usr/bin/env python3
"""
城市绿度体检 (NDVI 分析)
使用 Sentinel-2 数据计算城市植被覆盖率
"""

import ee
import geemap
import os
import sys
from datetime import datetime

def analyze_city_ndvi(city_name: str, year: int = None, output_dir: str = ".") -> dict:
    """
    分析城市植被覆盖率 (NDVI)

    Args:
        city_name: 城市名称 (如 "Beijing", "Shanghai")
        year: 分析年份，默认为当前年份
        output_dir: 输出目录

    Returns:
        dict: 包含 ndvi_mean, rating, map_path 的结果字典
    """
    # 初始化 Earth Engine
    PROJECT_ID = "project-37ebd001-5648-4239-916"
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)

    if year is None:
        year = datetime.now().year

    # 获取城市边界
    print(f"正在获取 {city_name} 的边界...")
    city_boundary = geemap.osm_to_ee(city_name, which_result=1)

    # 设置时间范围 (夏季数据更能反映植被状况)
    start_date = f"{year}-06-01"
    end_date = f"{year}-09-30"

    # 加载 Sentinel-2 SR Harmonized 数据
    print(f"正在加载 {year} 年 Sentinel-2 数据...")
    s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(city_boundary) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))

    # 云掩膜函数
    def mask_clouds(image):
        qa = image.select("QA60")
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11
        mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
            qa.bitwiseAnd(cirrus_bit_mask).eq(0)
        )
        return image.updateMask(mask).divide(10000)

    # 应用云掩膜并取中位数
    s2_masked = s2.map(mask_clouds)
    composite = s2_masked.median().clip(city_boundary)

    # 计算 NDVI: (NIR - Red) / (NIR + Red)
    # Sentinel-2: B8 = NIR, B4 = Red
    ndvi = composite.normalizedDifference(["B8", "B4"]).rename("NDVI")

    # 计算区域平均 NDVI
    print("正在计算平均 NDVI...")
    stats = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=city_boundary,
        scale=10,
        maxPixels=1e9
    )
    ndvi_mean = stats.get("NDVI").getInfo()

    # 评级
    if ndvi_mean >= 0.6:
        rating = "优"
        rating_desc = "植被覆盖非常好，绿化水平高"
    elif ndvi_mean >= 0.4:
        rating = "良"
        rating_desc = "植被覆盖较好，绿化水平中上"
    elif ndvi_mean >= 0.2:
        rating = "中"
        rating_desc = "植被覆盖一般，有提升空间"
    else:
        rating = "差"
        rating_desc = "植被覆盖较低，需加强绿化"

    # 创建可视化地图
    print("正在生成植被覆盖图...")
    Map = geemap.Map()
    Map.centerObject(city_boundary, 11)

    # NDVI 可视化参数 (绿色渲染)
    ndvi_vis = {
        "min": -0.1,
        "max": 0.8,
        "palette": [
            "#d73027",  # 红色 - 无植被
            "#fc8d59",  # 橙色
            "#fee08b",  # 黄色
            "#d9ef8b",  # 浅绿
            "#91cf60",  # 中绿
            "#1a9850"   # 深绿 - 高植被
        ]
    }

    Map.addLayer(ndvi, ndvi_vis, f"{city_name} NDVI {year}")
    Map.addLayer(city_boundary, {"color": "blue"}, "City Boundary", False)

    # 添加图例
    Map.add_colorbar(
        ndvi_vis,
        label="NDVI (植被指数)",
        layer_name=f"{city_name} NDVI {year}"
    )

    # 保存地图
    map_filename = f"{city_name.replace(' ', '_')}_ndvi_{year}.html"
    map_path = os.path.join(output_dir, map_filename)
    Map.to_html(map_path)
    print(f"地图已保存至: {map_path}")

    result = {
        "city": city_name,
        "year": year,
        "ndvi_mean": round(ndvi_mean, 4),
        "rating": rating,
        "rating_description": rating_desc,
        "map_path": map_path
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python city_ndvi_analysis.py <城市名称> [年份] [输出目录]")
        print("示例: python city_ndvi_analysis.py Beijing 2023 ./output")
        sys.exit(1)

    city_name = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    os.makedirs(output_dir, exist_ok=True)

    result = analyze_city_ndvi(city_name, year, output_dir)

    print("\n" + "=" * 50)
    print(f"城市绿度体检报告 - {result['city']}")
    print("=" * 50)
    print(f"分析年份: {result['year']}")
    print(f"平均 NDVI: {result['ndvi_mean']}")
    print(f"评级: {result['rating']}")
    print(f"评价: {result['rating_description']}")
    print(f"地图文件: {result['map_path']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
