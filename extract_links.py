import requests
import re
import base64
import html
from urllib.parse import urlparse, parse_qs, urlunparse

def advanced_deduplication(links):
    """
    对代理链接列表进行高级去重。
    如果两个链接的核心部分（协议、地址、端口）相同，
    则只保留参数最全（即字符串最长）的那个链接。
    """
    processed_links = {}
    
    for link in links:
        # 尝试将链接的参数和片段部分分开，以获取其“基础”部分
        # 例如: vless://...@host:port?params#name -> vless://...@host:port
        try:
            # 找到参数 '?' 或别名 '#' 的起始位置
            query_start = link.find('?')
            fragment_start = link.find('#')

            if query_start != -1 and fragment_start != -1:
                # 如果两者都存在，取最先出现的位置
                end_pos = min(query_start, fragment_start)
            elif query_start != -1:
                end_pos = query_start
            elif fragment_start != -1:
                end_pos = fragment_start
            else:
                end_pos = -1

            if end_pos != -1:
                base_link = link[:end_pos]
            else:
                base_link = link
        except Exception:
            # 如果解析失败，则将整个链接作为基础部分
            base_link = link

        # 核心去重逻辑：
        # 如果这个基础链接还没见过，或者当前链接比已记录的更长，就更新它
        if base_link not in processed_links or len(link) > len(processed_links[base_link]):
            processed_links[base_link] = link
            
    # 返回字典中存储的所有最终链接
    return list(processed_links.values())

def extract_proxy_links(url):
    """
    从给定的URL中提取 VLESS, VMess, 和 Hysteria2 链接，
    进行高级去重，然后生成一个订阅链接。
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text

        vless_links = re.findall(r'vless://[^\s<>"]+', content)
        vmess_links = re.findall(r'vmess://[^\s<>"]+', content)
        hysteria2_links = re.findall(r'hysteria2://[^\s<>"]+', content)

        if not vless_links and not vmess_links and not hysteria2_links:
            print("没有找到任何 VLESS, VMess, 或 Hysteria2 链接。")
            return None

        all_links = [html.unescape(link) for link in vless_links + vmess_links + hysteria2_links]

        # 使用新的高级去重函数
        unique_links = advanced_deduplication(all_links)

        print("\n--- 提取并去重后的结果 ---")
        print(f"总计保留 {len(unique_links)} 条独立链接:")
        for link in sorted(unique_links): # 排序后输出，更美观
            print(link)
        print("--------------------------")
        if len(unique_links) < len(all_links):
            print("已根据规则去除基础部分相同但较短的链接。")

        combined_links_str = "\n".join(unique_links)
        subscription_content_bytes = combined_links_str.encode('utf-8')
        subscription_link = base64.urlsafe_b64encode(subscription_content_bytes).decode('utf-8')

        return subscription_link

    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

if __name__ == "__main__":
    url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
    print(f"正在从以下地址抓取链接:\n{url}\n")
    
    result = extract_proxy_links(url)
    
    if result:
        try:
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(result)
            print("\n成功！订阅链接已写入文件: subscription.txt")
        except IOError as e:
            print(f"\n写入文件时出错: {e}")
