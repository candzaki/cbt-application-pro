import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Extract CSS HTML
css_match = re.search(r'st\.markdown\("""\n\s*<style>(.*?)</style>\n\s*""", unsafe_allow_html=True\)', content, re.DOTALL)
if css_match:
    with open("static/html/app_style.html", "w", encoding="utf-8") as f:
        f.write('<style>' + css_match.group(1) + '</style>')
    content = content.replace(css_match.group(0), 'with open("static/html/app_style.html", "r", encoding="utf-8") as f:\n        st.markdown(f.read(), unsafe_allow_html=True)')

# Extract bg_js
bg_match = re.search(r'bg_js = """\n(.*?)\n\s*"""', content, re.DOTALL)
if bg_match:
    with open("static/js/bg_animation.js", "w", encoding="utf-8") as f:
        f.write(bg_match.group(1))
    content = content.replace(bg_match.group(0), 'with open("static/js/bg_animation.js", "r", encoding="utf-8") as f:\n        bg_js = f.read()')

# Extract cheat_script
cheat_match = re.search(r'cheat_script = """\n(.*?)\n\s*"""', content, re.DOTALL)
if cheat_match:
    with open("static/js/anti_cheat.js", "w", encoding="utf-8") as f:
        f.write(cheat_match.group(1))
    content = content.replace(cheat_match.group(0), 'with open("static/js/anti_cheat.js", "r", encoding="utf-8") as f:\n        cheat_script = f.read()')

# Extract timer_js
timer_match = re.search(r'timer_js = f"""\n(.*?)\n\s*"""', content, re.DOTALL)
if timer_match:
    timer_content = timer_match.group(1).replace('{{', '{').replace('}}', '}')
    with open("static/js/timer.js", "w", encoding="utf-8") as f:
        f.write(timer_content)
    content = content.replace(timer_match.group(0), 'with open("static/js/timer.js", "r", encoding="utf-8") as f:\n        timer_js = f.read().replace("{remaining}", str(remaining))')

# Extract webcam_html
webcam_match = re.search(r'webcam_html = """\n(.*?)\n\s*"""', content, re.DOTALL)
if webcam_match:
    with open("static/html/webcam.html", "w", encoding="utf-8") as f:
        f.write(webcam_match.group(1))
    content = content.replace(webcam_match.group(0), 'with open("static/html/webcam.html", "r", encoding="utf-8") as f:\n        webcam_html = f.read()')

# Extract webcam_js
webcam_js_match = re.search(r'webcam_js = """\n(.*?)\n\s*"""', content, re.DOTALL)
if webcam_js_match:
    with open("static/js/webcam.js", "w", encoding="utf-8") as f:
        f.write(webcam_js_match.group(1))
    content = content.replace(webcam_js_match.group(0), 'with open("static/js/webcam.js", "r", encoding="utf-8") as f:\n        webcam_js = f.read()')


with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Extraction complete.")
