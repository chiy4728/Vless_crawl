import requests
import re
import base64
import html

def extract_proxy_links(url):
    """
    从给定的URL中提取 VLESS, VMess, 和 Hysteria2 链接，
    并将它们合并、去重、Base64编码后生成一个订阅链接。
    """
    try:
        # 1. 获取网页内容
        response = requests.get(url, timeout=10) # 增加超时设置
        response.raise_for_status()  # 如果请求失败则抛出异常
        content = response.text

        # 2. 使用正则表达式分别提取不同协议的链接
        # VLESS 链接正则
        vless_links = re.findall(r'vless://[^\s<>"]+', content)
        # VMess 链接正则
        vmess_links = re.findall(r'vmess://[^\s<>"]+', content)
        # Hysteria2 链接正则 (新增)
        hysteria2_links = re.findall(r'hysteria2://[^\s<>"]+', content)

        if not vless_links and not vmess_links and not hysteria2_links:
            print("没有找到任何 VLESS, VMess, 或 Hysteria2 链接。")
            return None

        # 3. 对链接进行 HTML 解码并合并
        decoded_vless_links = [html.unescape(link) for link in vless_links]
        decoded_vmess_links = [html.unescape(link) for link in vmess_links]
        decoded_hysteria2_links = [html.unescape(link) for link in hysteria2_links] # 新增

        # 将所有链接合并到一个列表中
        all_links = decoded_vless_links + decoded_vmess_links + decoded_hysteria2_links

        # 4. 去重
        unique_links = list(set(all_links))
        
        # (可选) 打印提取到的链接，方便调试
        print("\n--- 提取结果 ---")
        if decoded_vless_links:
            print(f"\n提取到 {len(set(decoded_vless_links))} 条独立的 VLESS 链接:")
            for link in sorted(list(set(decoded_vless_links))):
                print(link)
        if decoded_vmess_links:
            print(f"\n提取到 {len(set(decoded_vmess_links))} 条独立的 VMess 链接:")
            for link in sorted(list(set(decoded_vmess_links))):
                print(link)
        if decoded_hysteria2_links:
            print(f"\n提取到 {len(set(decoded_hysteria2_links))} 条独立的 Hysteria2 链接:")
            for link in sorted(list(set(decoded_hysteria2_links))):
                print(link)
        
        print("\n-----------------")
        print(f"总计提取到 {len(unique_links)} 条独立链接。")
        if len(unique_links) < len(all_links):
            print("已自动去除重复链接。")

        # 5. 合并并进行 Base64 编码
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
    # 目标URL，你可以替换成任何包含节点链接的页面
    url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
    
    print(f"正在从以下地址抓取链接:\n{url}\n")
    
    result = extract_proxy_links(url)
    
    if result:
        # 将结果写入文件
        try:
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(result)
            print("\n成功！订阅链接已写入文件: subscription.txt")
        except IOError as e:
            print(f"\n写入文件时出错: {e}")
