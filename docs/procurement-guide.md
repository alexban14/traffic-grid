# Hardware Procurement Guide: Mobile Proxy Tier

To build the high-trust physical layer of TrafficGrid, follow this procurement list.

## 1. Cellular Modems (Quantity: 3-5 to start)
- **Primary Choice:** [Huawei E3372h-607 / 153](https://www.google.com/search?q=Huawei+E3372+unlocked+HiLink)
  - *Note:* Ensure it says "HiLink" or "Unlocked". HiLink allows us to rotate the IP with a simple `curl` command to its internal API.
- **Alternative:** [ZTE MF833V 4G LTE](https://www.amazon.com/s?k=ZTE+MF833V)

## 2. Connectivity & Power (Mandatory)
- **Powered USB Hub:** [Sabrent 60W 10-Port USB 3.0 Hub](https://www.amazon.com/Sabrent-Aluminum-Individual-Switches-HB-MC3B/dp/B0797NZ5F8)
  - *Why:* Each 4G modem can pull up to 500mA-1A during peak transmission. Without a powered hub, your MeLe Q3Q will crash or the modems will cycle.

## 3. SIM Cards
- **Requirement:** Local data SIMs with flat-rate or high-cap data plans.
- **Tip:** Use providers that don't charge for "reconnecting" — we will be dropping and re-establishing the connection frequently to get new IPs.

## 4. Integration with MeLe Q3Q
- You are currently running on the MeLe. This is **not an issue** as long as we use the powered hub mentioned above.
- The MeLe's Celeron N5105 is plenty powerful to handle the proxy routing (SOCKS5 server) for 5-10 modems while still running NullClaw.