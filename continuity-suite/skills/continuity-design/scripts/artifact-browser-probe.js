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
  const measureContext = document.createElement("canvas").getContext("2d");
  const add = (rule_id, severity, element, evidence) => findings.push({
    rule_id, severity, status: "open", location: selector(element), evidence,
  });
  const rgba = (value) => {
    const match = value.match(/rgba?\(([^)]+)\)/);
    if (!match) return null;
    const parts = match[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    return parts.length >= 3 ? { r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1 } : null;
  };
  const luminance = ({ r, g, b }) => {
    const channel = (value) => {
      const normalized = value / 255;
      return normalized <= 0.04045 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
  };
  const contrast = (a, b) => {
    const light = Math.max(luminance(a), luminance(b));
    const dark = Math.min(luminance(a), luminance(b));
    return (light + 0.05) / (dark + 0.05);
  };
  const opaqueBackground = (element) => {
    let current = element;
    while (current) {
      const color = rgba(getComputedStyle(current).backgroundColor);
      if (color && color.a >= 0.95) return color;
      current = current.parentElement;
    }
    return rgba(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
  };
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
    const clipsX = ["hidden", "clip", "auto", "scroll"].includes(style.overflowX);
    const clipsY = ["hidden", "clip", "auto", "scroll"].includes(style.overflowY);
    if ((clipsX && element.scrollWidth > element.clientWidth + 1) || (clipsY && element.scrollHeight > element.clientHeight + 1)) {
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
    measureContext.font = style.font;
    const characterWidth = measureContext.measureText("0").width;
    const characterMeasure = rect.width / Math.max(characterWidth, 1);
    if ((element.tagName === "P" || element.tagName === "LI") && lineCount >= 3 && characterMeasure > 75) {
      add("body-measure", "warning", element, `approximately ${characterMeasure.toFixed(1)}ch across`);
    }
  }
  for (const element of [...document.querySelectorAll("button, input, select, textarea, a[href]")].filter(visible)) {
    const rect = element.getBoundingClientRect();
    if (rect.width < 24 || rect.height < 24) add("target-size", "error", element, `${Math.round(rect.width)}x${Math.round(rect.height)}px target`);
    else if (rect.width < 44 || rect.height < 44) add("target-size", "warning", element, `${Math.round(rect.width)}x${Math.round(rect.height)}px target`);
    const accessibleName = element.getAttribute("aria-label") || element.getAttribute("title") || element.textContent.trim() || element.value || (element.id && document.querySelector(`label[for="${CSS.escape(element.id)}"]`)?.textContent.trim());
    if (!accessibleName) add("accessible-name", "error", element, "Interactive control has no accessible name");
  }
  for (const element of [...document.querySelectorAll("h1, h2, h3, p, li, label, button, a, td, th, span, strong, small")].filter(visible)) {
    if (!element.textContent.trim()) continue;
    const style = getComputedStyle(element);
    const foreground = rgba(style.color);
    const background = opaqueBackground(element);
    if (!foreground || foreground.a < 0.95 || !background) continue;
    const ratio = contrast(foreground, background);
    const fontSize = Number.parseFloat(style.fontSize);
    const fontWeight = Number.parseInt(style.fontWeight, 10) || 400;
    const large = fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700);
    const required = large ? 3 : 4.5;
    if (ratio + 0.01 < required) add("color-contrast", "error", element, `${ratio.toFixed(2)}:1 contrast; requires ${required}:1`);
  }
  for (const element of [...document.querySelectorAll('[role="button"], [onclick]')].filter(visible)) {
    if (!element.matches("button, a[href], input[type=button], input[type=submit]")) {
      add("semantic-control", "error", element, "Clickable behavior is not represented by a native interactive control");
    }
  }
  const animated = [...document.querySelectorAll("body *")].filter((element) => {
    const style = getComputedStyle(element);
    return visible(element) && (style.animationName !== "none" || style.transitionDuration.split(",").some((value) => Number.parseFloat(value) > 0));
  });
  const authoredStyles = [...document.querySelectorAll("style")].map((item) => item.textContent).join("\n");
  if (animated.length && !/prefers-reduced-motion/i.test(authoredStyles)) {
    add("reduced-motion", "error", animated[0], `${animated.length} animated elements have no authored reduced-motion treatment`);
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
