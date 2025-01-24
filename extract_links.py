import requests
import re
import base64
import html

def extract_vless_vmess_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        vless_links = re.findall(
            r'vless://[^\s<>"]+\?[^\s<>"]+#?[^\s<>"]*', content
        )
        vmess_links = re.findall(
            r'vmess://[^\s<>"]+', content
        )

        if not vless_links and not vmess_links:
            print("No VLESS or VMess links found.")
            return None

        decoded_vless_links = [html.unescape(link) for link in vless_links]
        decoded_vmess_links = [html.unescape(link) for link in vmess_links]

        # 去重链接
        unique_vless_links = set(decoded_vless_links)
        unique_vmess_links = set(decoded_vmess_links)
        unique_links = list(unique_vless_links.union(unique_vmess_links))

        print("\n提取的 VLESS 链接:")
        for link in unique_vless_links:
            print(link)
        print("\n提取的 VMESS 链接:")
        for link in unique_vmess_links:
            print(link)
        if len(unique_links) < (len(decoded_vless_links) + len(decoded_vmess_links)):
            print("Duplicate links found and removed.")

        combined_links = list(unique_links) # 将去重后的链接列表化
        print("\n去重后的链接:")
        for link in combined_links:
            print(link)

        vless_vmess_combined = "\n".join(combined_links)
        subscription_link = base64.urlsafe_b64encode(vless_vmess_combined.encode()).decode()

        return subscription_link

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
    result = extract_vless_vmess_links(url)
    if result:
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("Subscription link written to subscription.txt")
