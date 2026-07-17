import asyncio
import httpx
import re

async def test_ddg():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get("https://html.duckduckgo.com/html/?q=ipl+2026+winner", headers=headers)
        
        # Match the title and snippet inside each result block
        blocks = re.findall(r'<div class="[^"]*result__body[^"]*">([\s\S]*?)</div>\s*</div>\s*</div>', res.text)
        print("Blocks:", len(blocks))
        
        for i, block in enumerate(blocks[:5]):
            title_match = re.search(r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*>([\s\S]*?)</a>', block)
            snippet_match = re.search(r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>([\s\S]*?)</a>', block)
            
            if title_match and snippet_match:
                title = re.sub(r'<[^>]+>', "", title_match.group(1)).strip()
                snippet = re.sub(r'<[^>]+>', "", snippet_match.group(1)).strip()
                print(f"Vector {i+1}: {title} -> {snippet}")
                print("-" * 20)

asyncio.run(test_ddg())
