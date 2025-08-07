#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫 - 使用DrissionPage库
功能：访问小红书页面，等待30秒后搜索"安吉深蓝计划"，获取搜索结果URL并保存到Excel
"""

from DrissionPage import ChromiumPage
import time
import pandas as pd
from datetime import datetime
import os

def get_search_results_urls(page, collected_urls):
    """
    获取当前页面的搜索结果URL
    """
    urls = []
    
    # 尝试多种可能的搜索结果链接选择器
    result_selectors = [
        'a[href*="/explore/"]',
        'a[href*="/discovery/"]',
        'a[href*="/item/"]',
        'a[href*="/note/"]',
        '.note-item a',
        '.search-result-item a',
        '[data-testid="note-item"] a',
        '.note-card a',
        'a[class*="note"]',
        'a[class*="item"]',
        '.feed-item a',
        '.content-item a',
        'a[href*="xiaohongshu.com"]',
        'a[target="_blank"]',
        'a[rel="noopener"]'
    ]
    
    for selector in result_selectors:
        try:
            elements = page.eles(selector, timeout=5)
            if elements:
                print(f"找到搜索结果元素，使用选择器: {selector}，共找到 {len(elements)} 个元素")
                for i, element in enumerate(elements):
                    try:
                        url = element.link
                        if url and url not in collected_urls and 'xiaohongshu.com' in url:
                            urls.append(url)
                            print(f"获取到URL #{len(urls)}: {url}")
                    except:
                        try:
                            # 尝试获取href属性
                            url = element.attr('href')
                            if url and url not in collected_urls and 'xiaohongshu.com' in url:
                                urls.append(url)
                                print(f"获取到URL #{len(urls)}: {url}")
                        except:
                            continue
                if urls:
                    break
        except Exception as e:
            print(f"选择器 {selector} 出错: {e}")
            continue
    
    # 如果没有找到URL，尝试调试模式
    if not urls:
        print("未找到URL，尝试调试模式...")
        try:
            # 获取所有链接
            all_links = page.eles('a', timeout=3)
            print(f"页面上共有 {len(all_links)} 个链接")
            for i, link in enumerate(all_links[:10]):  # 只显示前10个
                try:
                    href = link.attr('href')
                    text = link.text
                    print(f"链接 {i+1}: href={href}, text={text[:50]}")
                except:
                    continue
            
            # 尝试获取所有可能的容器元素
            containers = page.eles('div, article, section', timeout=3)
            print(f"页面上共有 {len(containers)} 个容器元素")
            
            # 尝试查找包含特定文本的元素
            note_elements = page.eles('*', timeout=3)
            note_count = 0
            for elem in note_elements:
                try:
                    text = elem.text
                    if text and ('安吉' in text or '深蓝' in text or '计划' in text):
                        note_count += 1
                        if note_count <= 5:
                            print(f"找到相关内容元素: {text[:100]}")
                except:
                    continue
            print(f"找到 {note_count} 个包含相关内容的元素")
            
        except Exception as e:
            print(f"调试模式出错: {e}")
    
    return urls

def scroll_page_half(page):
    """
    将页面向下滚动半页
    """
    try:
        # 获取当前页面高度
        page_height = page.run_js('return document.body.scrollHeight')
        current_position = page.run_js('return window.pageYOffset')
        
        # 滚动到页面的一半位置
        scroll_to = current_position + (page_height // 4)
        page.run_js(f'window.scrollTo(0, {scroll_to})')
        
        print("页面已向下滚动半页")
        time.sleep(2)  # 等待页面加载
        return True
    except Exception as e:
        print(f"滚动页面时出错: {e}")
        return False

def save_urls_to_excel(urls, filename=None):
    """
    将URL保存到Excel文件
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"xiaohongshu_urls_{timestamp}.xlsx"
    
    # 创建DataFrame
    df = pd.DataFrame({
        '序号': range(1, len(urls) + 1),
        'URL': urls,
        '获取时间': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(urls)
    })
    
    # 保存到Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"已保存 {len(urls)} 个URL到文件: {filename}")
    return filename

def main():
    """
    主函数：访问小红书并搜索指定内容，获取URL并保存到Excel
    """
    collected_urls = set()  # 用于查重的URL集合
    all_urls = []  # 所有收集到的URL列表
    
    try:
        # 创建浏览器页面对象，设置保留窗口
        page = ChromiumPage()
        
        print("正在启动浏览器...")
        
        # 访问小红书首页
        print("正在访问小红书首页...")
        page.get('https://www.xiaohongshu.com')
        
        # 等待5秒
        print("等待5秒...")
        time.sleep(5)
        
        # 查找搜索框并输入搜索内容
        print("正在搜索'安吉深蓝计划'...")
        
        # 尝试多种可能的搜索框选择器
        search_selectors = [
            'input[placeholder*="搜索"]',
            'input[type="search"]',
            '.search-input',
            '[data-testid="search-input"]',
            'input[name="search"]',
            '.search-box input',
            'input[class*="search"]'
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                search_input = page.ele(selector, timeout=3)
                if search_input:
                    print(f"找到搜索框，使用选择器: {selector}")
                    break
            except:
                continue
        
        if search_input:
            # 清空搜索框并输入搜索内容
            search_input.clear()
            search_input.input('安吉深蓝计划')
            
            # 查找搜索按钮并点击
            search_button_selectors = [
                'button[type="submit"]',
                '.search-btn',
                '[data-testid="search-button"]',
                'button[class*="search"]',
                'input[type="submit"]'
            ]
            
            search_button = None
            for selector in search_button_selectors:
                try:
                    search_button = page.ele(selector, timeout=3)
                    if search_button:
                        print(f"找到搜索按钮，使用选择器: {selector}")
                        break
                except:
                    continue
            
            if search_button:
                search_button.click()
                print("搜索完成！")
            else:
                # 如果找不到搜索按钮，尝试按回车键
                search_input.click()
                search_input.input('\n')  # 使用换行符模拟回车键
                print("通过回车键执行搜索")
            
            # 等待搜索结果加载
            print("等待搜索结果加载...")
            time.sleep(15)
            
            # 开始获取所有section的href
            print("开始获取所有section的href...")
            
            all_urls = []  # 存储所有唯一的URL
            collected_urls = set()  # 用于查重
            scroll_count = 0  # 滚动次数
            last_first_url = None  # 记录上一次section[1]的URL
            same_first_url_count = 0  # 连续相同URL的次数
            
            while True:
                print(f"\n=== 第 {scroll_count + 1} 次滚动 ===")
                
                # 获取当前页面section[1]到section[20]的href
                current_page_urls = []
                for section_num in range(1, 21):
                    xpath = f'/html/body/div[2]/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/section[{section_num}]/div/a[2]'
                    
                    try:
                        element = page.ele(f'xpath:{xpath}', timeout=3)
                        if element:
                            href = element.attr('href')
                            if not href:
                                # 尝试使用JavaScript获取href
                                try:
                                    href = page.run_js(f'return document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.href')
                                except:
                                    href = None
                            
                            if href and '/search_result/' in href and href not in collected_urls:
                                collected_urls.add(href)
                                all_urls.append(href)
                                current_page_urls.append(href)
                                print(f"Section[{section_num}] href: {href}")
                            elif href and '/search_result/' in href:
                                print(f"Section[{section_num}] href: {href} (重复，跳过)")
                            else:
                                print(f"Section[{section_num}]: 未找到有效href")
                        else:
                            print(f"Section[{section_num}]: 元素不存在")
                    except Exception as e:
                        print(f"Section[{section_num}] 出错: {e}")
                
                print(f"本次获取到 {len(current_page_urls)} 个新URL")
                print(f"总共已收集 {len(all_urls)} 个唯一URL")
                
                # 检查section[1]的URL是否与上次相同
                if current_page_urls and len(current_page_urls) > 0:
                    current_first_url = current_page_urls[0]
                    if current_first_url == last_first_url:
                        same_first_url_count += 1
                        print(f"Section[1] URL相同，连续次数: {same_first_url_count}")
                    else:
                        same_first_url_count = 0
                        print(f"Section[1] URL不同，重置计数器")
                    
                    last_first_url = current_first_url
                else:
                    # 如果没有获取到任何URL，也检查section[1]是否重复
                    try:
                        section1_xpath = '/html/body/div[2]/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/section[1]/div/a[2]'
                        section1_element = page.ele(f'xpath:{section1_xpath}', timeout=3)
                        if section1_element:
                            section1_href = section1_element.attr('href')
                            if not section1_href:
                                section1_href = page.run_js(f'return document.evaluate("{section1_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.href')
                            
                            if section1_href and section1_href == last_first_url:
                                same_first_url_count += 1
                                print(f"Section[1] URL相同（无新URL），连续次数: {same_first_url_count}")
                            elif section1_href and section1_href != last_first_url:
                                same_first_url_count = 0
                                print(f"Section[1] URL不同（无新URL），重置计数器")
                                last_first_url = section1_href
                    except:
                        pass
                
                # 如果连续3次section[1]的URL都相同，说明已经翻到底
                if same_first_url_count >= 3:
                    print("连续3次section[1]的URL相同，已翻到底，停止获取")
                    break
                
                # 滚动页面
                print("滚动页面以加载更多内容...")
                try:
                    # 使用固定的滚动距离（页面高度的20%）
                    scroll_distance = 800  # 固定滚动800像素
                    current_position = page.run_js('return window.pageYOffset')
                    scroll_to = current_position + scroll_distance
                    page.run_js(f'window.scrollTo(0, {scroll_to})')
                    print(f"页面已向下滚动 {scroll_distance} 像素")
                    time.sleep(3)  # 等待页面加载
                except Exception as e:
                    print(f"滚动页面时出错: {e}")
                    break
                
                scroll_count += 1
        else:
            print("未找到搜索框，请手动搜索")
        
        # 保存URL到Excel
        if all_urls:
            filename = save_urls_to_excel(all_urls)
            print(f"\n总共获取到 {len(all_urls)} 个唯一URL")
            print(f"已保存到文件: {filename}")
        else:
            print("没有获取到任何URL")
        
        # 保持浏览器窗口打开
        print("\n爬虫任务完成，浏览器窗口将保持打开状态...")
        print("按 Ctrl+C 可以关闭浏览器")
        
        # 无限循环保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n用户中断程序，正在关闭浏览器...")
        page.quit()
        print("浏览器已关闭")
    except Exception as e:
        print(f"发生错误: {e}")
        print("浏览器窗口将保持打开状态，请手动关闭")
        # 即使发生错误也保持浏览器窗口打开
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main() 