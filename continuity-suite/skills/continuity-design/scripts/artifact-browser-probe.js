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
  const selector = (element) => {
    if (element.id) return `#${CSS.escape(element.id)}`;
    const classes = [...element.classList].slice(0, 2).map((name) => `.${CSS.escape(name)}`).join("");
    return `${element.tagName.toLowerCase()}${classes}`;
  };
  const findings = [];
  const add = (rule_id, severity, element, evidence) => findings.push({
    rule_id, severity, status: "open", location: selector(element), evidence,
  });
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
  for (const element of [...document.querySelectorAll("h1, h2, h3, p, li, label, button, a")].filter(visible)) {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    if (element.scrollWidth > element.clientWidth + 1 || element.scrollHeight > element.clientHeight + 1) {
      add("text-clipping", "error", element, `scroll ${element.scrollWidth}x${element.scrollHeight}; client ${element.clientWidth}x${element.clientHeight}`);
    }
    const fontSize = Number.parseFloat(style.fontSize);
    const lineHeight = Number.parseFloat(style.lineHeight);
    const lineCount = lineHeight > 0 ? Math.round(rect.height / lineHeight) : 1;
    if (/^H[1-3]$/.test(element.tagName) && fontSize > Math.min(96, viewport.width * 0.18)) {
      add("display-size-ceiling", "warning", element, `${fontSize}px display type at ${viewport.width}px viewport width`);
    }
    if (/^H[1-3]$/.test(element.tagName) && Number.parseFloat(style.letterSpacing) < -0.04 * fontSize) {
      add("display-tracking", "warning", element, `${style.letterSpacing} tracking at ${fontSize}px font size`);
    }
    if ((element.tagName === "P" || element.tagName === "LI") && lineCount >= 3 && rect.width / Math.max(fontSize, 1) > 42) {
      add("body-measure", "warning", element, `approximately ${(rect.width / Math.max(fontSize, 1)).toFixed(1)} font-size units across`);
    }
  }
  for (const element of [...document.querySelectorAll("button, input, select, textarea, a[href]")].filter(visible)) {
    const rect = element.getBoundingClientRect();
    if (rect.width < 24 || rect.height < 24) add("target-size", "error", element, `${Math.round(rect.width)}x${Math.round(rect.height)}px target`);
    else if (rect.width < 44 || rect.height < 44) add("target-size", "warning", element, `${Math.round(rect.width)}x${Math.round(rect.height)}px target`);
  }
  for (let index = 0; index < protectedContent.length; index += 1) {
    const a = protectedContent[index];
    const aRect = a.getBoundingClientRect();
    for (let other = index + 1; other < protectedContent.length; other += 1) {
      const b = protectedContent[other];
      if (a.contains(b) || b.contains(a)) continue;
      const bRect = b.getBoundingClientRect();
      if (overlaps(aRect, bRect)) add("content-collision", "error", a, `overlaps ${selector(b)}`);
    }
  }
  return {
    schema_version: 2,
    viewport,
    document: { scroll_width: root.scrollWidth, client_width: root.clientWidth },
    horizontal_overflow: horizontalOverflow,
    sticky_or_fixed_obstructions: obstructions,
    craft_findings: findings,
    passed: !horizontalOverflow && obstructions.length === 0 && !findings.some((item) => item.severity === "error" || item.severity === "critical"),
  };
})();
