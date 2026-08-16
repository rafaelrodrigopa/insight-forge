import os
from app.publish.publishers.linkedin_publisher import LinkedInFormatter

posts_dir = 'posts'
for fname in sorted(os.listdir(posts_dir)):
    if fname.endswith('.md'):
        path = os.path.join(posts_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        formatted = LinkedInFormatter.format_for_linkedin(content)
        print(f"=== {fname} ===")
        print(f"Original len: {len(content)} | Formatted len: {len(formatted)}")
        print("LAST 250 CHARS:")
        print(repr(formatted[-250:]))
        print("="*60)
