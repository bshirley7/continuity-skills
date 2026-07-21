(() => {
  const viewport = { width: window.innerWidth, height: window.innerHeight };
  const root = document.documentElement;
  const horizontalOverflow = root.scrollWidth > root.clientWidth + 1;
  const visible = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
  };
  const overlaps = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
  const fixed = [...document.querySelectorAll("body *")].filter((element) => {
    const position = getComputedStyle(element).position;
    return visible(element) && (position === "fixed" || position === "sticky");
  });
  const protectedContent = [...document.querySelectorAll("main a, main button, main input, main select, main textarea, main [tabindex], main h1, main h2, main h3, main p")].filter(visible);
  const obstructions = [];
  for (const overlay of fixed) {
    const overlayRect = overlay.getBoundingClientRect();
    for (const content of protectedContent) {
      if (overlay.contains(content) || content.contains(overlay)) continue;
      const contentRect = content.getBoundingClientRect();
      if (overlaps(overlayRect, contentRect)) {
        obstructions.push({
          overlay: overlay.tagName.toLowerCase() + (overlay.id ? `#${overlay.id}` : ""),
          content: content.tagName.toLowerCase() + (content.id ? `#${content.id}` : ""),
        });
      }
    }
  }
  return {
    schema_version: 1,
    viewport,
    document: { scroll_width: root.scrollWidth, client_width: root.clientWidth },
    horizontal_overflow: horizontalOverflow,
    sticky_or_fixed_obstructions: obstructions,
    passed: !horizontalOverflow && obstructions.length === 0,
  };
})();
