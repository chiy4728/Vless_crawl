import requests
import re
import base64
import html

def extract_vless_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        vless_links = re.findall(
            r'vless://[^\s<>"]+\?[^\s<>"]+#?[^\s<>"]*', content
        )

        if not vless_links:
            print("No VLESS links found.")
            return None

        decoded_links = [html.unescape(link) for link in vless_links]

        vless_combined = "\n".join(decoded_links)
        subscription_link = base64.urlsafe_b64encode(vless_combined.encode()).decode()

        return subscription_link

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
    result = extract_vless_links(url)
    if result:
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("Subscription link written to subscription.txt")
