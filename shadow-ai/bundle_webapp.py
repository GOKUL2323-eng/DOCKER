import os
import base64
import re

def bundle():
    frontend_dir = 'frontend'
    output_file = 'shadow_ai_complete.html'
    
    # Read core files
    with open(os.path.join(frontend_dir, 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()
        
    with open(os.path.join(frontend_dir, 'index.css'), 'r', encoding='utf-8') as f:
        css = f.read()
        
    # Order matters for JS injection
    with open(os.path.join(frontend_dir, 'authLogic.js'), 'r', encoding='utf-8') as f:
        auth_js = f.read()
        
    with open(os.path.join(frontend_dir, 'chatLogic.js'), 'r', encoding='utf-8') as f:
        chat_js = f.read()
        
    with open(os.path.join(frontend_dir, 'app.js'), 'r', encoding='utf-8') as f:
        app_js = f.read()
        
    # Read and encode avatar
    avatar_path = os.path.join(frontend_dir, 'assets', 'shadow_ninja_red.png')
    with open(avatar_path, 'rb') as f:
        avatar_b64 = base64.b64encode(f.read()).decode()
    
    # Assembly
    # 1. Inject CSS - Handle versioned paths
    html = re.sub(r'<link rel="stylesheet" href="/files/index.css\?v=[\d\.]+">', f'<style>\n{css}\n</style>', html)
    
    # 2. Inject JS
    js_bundle = f"<script>\n{auth_js}\n{chat_js}\n{app_js}\n</script>"
    
    # Remove existing script tags - Handle versioned paths
    html = re.sub(r'<script src="/files/authLogic.js\?v=[\d\.]+"></script>', '', html)
    html = re.sub(r'<script src="/files/chatLogic.js\?v=[\d\.]+"></script>', '', html)
    html = re.sub(r'<script src="/files/app.js\?v=[\d\.]+"></script>', '', html)
    
    # Inject combined JS before </body>
    html = html.replace('</body>', f'{js_bundle}\n</body>')
    
    # 3. Replace Image paths with Data URI
    html = html.replace('/files/assets/shadow_ninja_red.png', f'data:image/png;base64,{avatar_b64}')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Successfully bundled into {output_file}")

if __name__ == "__main__":
    bundle()
