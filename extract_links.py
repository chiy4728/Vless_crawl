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
            # 对于 vmess:// 链接，因为后面是 Base64 blob，没有明文的 ? 或 #，
            # 所以这里的逻辑会将整个 VMess 链接视为基础部分。
            # 这意味着 VMess 目前仅支持“完全一致”的去重，这对于 Base64 链接是合理的。
            
            query_start = link.find('?')
            fragment_start = link.find('#')

            if query_start != -1 and fragment_start != -1:
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
            base_link = link

        # 核心去重逻辑
        if base_link not in processed_links or len(link) > len(processed_links[base_link]):
            processed_links[base_link] = link
            
    return list(processed_links.values())

def extract_proxy_links(url):
    """
    从给定的URL中提取 VLESS, VMess (包含 URL Scheme 和 Raw Base64), 和 Hysteria2 链接，
    进行高级去重，然后生成一个订阅链接。
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text

        # 1. 提取标准的带协议头的链接
        vless_links = re.findall(r'vless://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+', content)
        vmess_links = re.findall(r'vmess://[a-zA-Z0-9+/=]+', content)
        hysteria2_links = re.findall(r'hysteria2://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+', content)

        # 2. 新增：提取不带协议头的 Raw Base64 VMess 节点
        # 特征：以 'ew' (JSON '{') 或 'ey' (JSON '{"') 开头，包含 Base64 字符，长度至少 50
        # 这样可以抓取你提供的 "ew0KICAidiI6..." 格式
        raw_vmess_matches = re.findall(r'(?:[^a-zA-Z0-9+/=]|^)((?:ew|ey)[a-zA-Z0-9+/=]{50,})(?:[^a-zA-Z0-9+/=]|$)', content)
        
        # 将提取到的 Raw Base64 转换为标准的 vmess:// 链接
        converted_vmess_links = []
        for raw_link in raw_vmess_matches:
            # 清理可能存在的换行符（虽然正则排除了，但以防 HTML 实体干扰）
            clean_link = raw_link.strip()
            if clean_link:
                converted_vmess_links.append(f"vmess://{clean_link}")
        
        if len(converted_vmess_links) > 0:
            print(f"发现 {len(converted_vmess_links)} 个不带协议头的 VMess Base64 节点，已自动添加协议头。")

        # 合并所有链接
        all_raw_links = vless_links + vmess_links + hysteria2_links + converted_vmess_links
        
        if not all_raw_links:
            print("没有找到任何有效节点链接。")
            return None

        # HTML 解码 (处理 &amp; 等字符)
        all_links = [html.unescape(link) for link in all_raw_links]

        # 执行去重
        unique_links = advanced_deduplication(all_links)

        print("\n--- 提取并去重后的结果 ---")
        print(f"总计保留 {len(unique_links)} 条独立链接:")
        # 简单的分类统计打印
        vless_c = sum(1 for l in unique_links if l.startswith('vless'))
        vmess_c = sum(1 for l in unique_links if l.startswith('vmess'))
        hy2_c = sum(1 for l in unique_links if l.startswith('hysteria2'))
        print(f"(VLESS: {vless_c}, VMess: {vmess_c}, Hysteria2: {hy2_c})")
        
        print("--------------------------")

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
    # 你的目标 URL
    url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
    print(f"正在从以下地址抓取链接:\n{url}\n")
    
    result = extract_proxy_links(url)
    
    if result:
        try:
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(result)
            print("\n成功！订阅链接已写入文件: subscription.txt")
            # 简单的预览（如果链接太长就不打印了）
            if len(result) < 200:
                print(f"订阅内容预览: {result}")
            else:
                print("订阅内容较长，请查看文件。")
        except IOError as e:
            print(f"\n写入文件时出错: {e}")
