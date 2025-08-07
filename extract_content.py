#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书内容提取器
功能：读取Excel文件中的URL，访问每个页面提取用户名称、标题和内容，保存为txt文件
"""

from DrissionPage import ChromiumPage
import pandas as pd
import os
import time
import re
from datetime import datetime

def clean_filename(filename):
    """
    清理文件名，移除非法字符
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    # 限制文件名长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def extract_page_content(page, url):
    """
    提取页面中的用户名称、标题和内容
    """
    try:
        # 等待页面加载
        time.sleep(3)
        
        # 提取用户名称（带重试机制）
        username = None
        username_xpath = '/html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[4]/div[1]/div/div[1]/a[2]/span'
        retry_count = 0
        while retry_count < 3:
            try:
                username_element = page.ele(f'xpath:{username_xpath}', timeout=5)
                if username_element:
                    username = username_element.text
                    print(f"用户名称: {username}")
                    break
                else:
                    print(f"未找到用户名称元素，重试 {retry_count + 1}/3")
                    retry_count += 1
                    if retry_count < 3:
                        print("等待60秒后重试...")
                        time.sleep(60)
            except Exception as e:
                print(f"获取用户名称失败: {e}")
                retry_count += 1
                if retry_count < 3:
                    print("等待60秒后重试...")
                    time.sleep(60)
        
        if not username:
            print("用户名称获取失败，已重试3次")
        
        # 提取标题
        title = None
        title_xpath = '/html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[4]/div[2]/div[1]/div[1]'
        try:
            title_element = page.ele(f'xpath:{title_xpath}', timeout=5)
            if title_element:
                title = title_element.text
                print(f"标题: {title}")
        except Exception as e:
            print(f"获取标题失败: {e}")
        
        # 提取内容
        content = None
        content_xpath = '/html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[4]/div[2]/div[1]/div[2]/span/span[1]'
        try:
            content_element = page.ele(f'xpath:{content_xpath}', timeout=5)
            if content_element:
                content = content_element.text
                print(f"内容长度: {len(content) if content else 0}")
        except Exception as e:
            print(f"获取内容失败: {e}")
        
        return username, title, content
        
    except Exception as e:
        print(f"提取页面内容时出错: {e}")
        return None, None, None

def save_to_txt(username, title, content, url, folder_path):
    """
    保存内容到txt文件
    """
    try:
        # 清理文件名
        if username and title:
            filename = f"{username}——{title}"
        elif username:
            filename = f"{username}——无标题"
        elif title:
            filename = f"未知用户——{title}"
        else:
            filename = f"未知内容_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filename = clean_filename(filename)
        file_path = os.path.join(folder_path, f"{filename}.txt")
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n")
            f.write(f"内容:\n{content or '无内容'}\n")
        
        print(f"已保存到文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return False

def main():
    """
    主函数
    """
    # 创建final文件夹
    folder_path = "final"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"创建文件夹: {folder_path}")
    
    # 读取Excel文件
    excel_file = "xiaohongshu_urls.xlsx"
    if not os.path.exists(excel_file):
        print(f"Excel文件不存在: {excel_file}")
        return
    
    try:
        df = pd.read_excel(excel_file)
        urls = df['URL'].tolist()
        print(f"从Excel文件中读取到 {len(urls)} 个URL")
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return
    
    # 创建浏览器页面对象
    page = ChromiumPage()
    
    try:
        # 遍历所有URL
        for i, url in enumerate(urls, 1):
            print(f"\n=== 处理第 {i}/{len(urls)} 个URL ===")
            print(f"URL: {url}")
            
            try:
                # 访问页面
                page.get(url)
                print("页面加载完成")
                
                # 提取内容
                username, title, content = extract_page_content(page, url)
                
                # 保存到txt文件
                if username or title or content:
                    success = save_to_txt(username, title, content, url, folder_path)
                    if success:
                        print(f"第 {i} 个txt文件生成成功！")
                    else:
                        print(f"第 {i} 个txt文件生成失败！")
                else:
                    print("未提取到任何内容")
                
                # 处理完一个URL后停留5秒
                if i < len(urls):
                    print("等待5秒后处理下一个URL...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"处理URL时出错: {e}")
                continue
        
        print(f"\n所有 {len(urls)} 个URL处理完成！")
        
        # 保持浏览器窗口打开
        print("浏览器窗口将保持打开状态...")
        print("按 Ctrl+C 可以关闭浏览器")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n用户中断程序，正在关闭浏览器...")
        page.quit()
        print("浏览器已关闭")
    except Exception as e:
        print(f"发生错误: {e}")
        print("浏览器窗口将保持打开状态，请手动关闭")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main() 