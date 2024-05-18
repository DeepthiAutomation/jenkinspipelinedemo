extract_between = lambda text, start, end: text[text.find(start) + len(start):text.find(end, text.find(start) + len(start))] if text.find(start) != -1 and text.find(end, text.find(start) + len(start)) != -1 else None
text = "Here is some <tag>content</tag> in the text."
start = "<tag>"
end = "</tag>"
content = extract_between(text, start, end)
print(content)  # Output: content
