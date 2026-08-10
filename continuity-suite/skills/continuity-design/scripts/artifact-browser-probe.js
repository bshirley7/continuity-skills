(() => {
  const viewport = { width: window.innerWidth, height: window.innerHeight };
  const root = document.documentElement;
  const horizontalOverflow = root.scrollWidth > root.clientWidth + 1;
  const visible = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && Number.parseFloat(style.opacity) > 0.01 && rect.width > 0 && rect.height > 0;
  };
  const viewportIntersectionRatio = (rect) => {
    const width = Math.max(0, Math.min(rect.right, viewport.width) - Math.max(rect.left, 0));
    const height = Math.max(0, Math.min(rect.bottom, viewport.height) - Math.max(rect.top, 0));
    const area = Math.max(rect.width * rect.height, 1);
    return (width * height) / area;
  };
  const overlaps = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
  const selector = (element) => {
    if (element.id) return `#${CSS.escape(element.id)}`;
    const classes = [...element.classList].slice(0, 2).map((name) => `.${CSS.escape(name)}`).join("");
    return `${element.tagName.toLowerCase()}${classes}`;
  };
  const findings = [];
  const measureContext = typeof document.createElement === "function"
    ? document.createElement("canvas").getContext("2d")
    : null;
  const add = (rule_id, severity, element, evidence) => findings.push({
    rule_id, severity, status: "open", location: selector(element), evidence,
  });
  const compositionPlanes = [...document.querySelectorAll("[data-continuity-composition-plane]")].map((element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const image = element instanceof HTMLImageElement ? element : null;
    const video = element instanceof HTMLVideoElement ? element : null;
    const backgroundMatch = style.backgroundImage.match(/^url\(["']?(.*?)["']?\)$/);
    return {
      plane_id: element.getAttribute("data-continuity-composition-plane"),
      selector: selector(element),
      tag_name: element.tagName.toLowerCase(),
      computed_z_index: Number.parseInt(style.zIndex, 10),
      visible: visible(element),
      asset_url: image?.currentSrc || image?.src || video?.currentSrc || video?.src || backgroundMatch?.[1] || null,
      load_complete: image ? image.complete && image.naturalWidth > 0 : video ? video.readyState >= 1 : true,
      natural_width: image?.naturalWidth || video?.videoWidth || null,
      natural_height: image?.naturalHeight || video?.videoHeight || null,
      object_position: style.objectPosition,
      background_position: style.backgroundPosition,
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    };
  });
  const typographyTransfers = [...document.querySelectorAll("[data-continuity-type-transfer]")].map((element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const copy = element.textContent.trim();
    const fontSize = Number.parseFloat(style.fontSize);
    const lineHeight = Number.parseFloat(style.lineHeight);
    if (measureContext) measureContext.font = style.font;
    const cap = measureContext?.measureText("H");
    const requestedFamily = style.fontFamily.split(",")[0].trim().replace(/^['"]|['"]$/g, "");
    const matchingFaces = [...document.fonts].filter((face) => face.family.replace(/^['"]|['"]$/g, "") === requestedFamily);
    return {
      transfer_id: element.getAttribute("data-continuity-type-transfer"),
      selector: selector(element),
      rendered_copy: copy,
      computed_family: style.fontFamily,
      font_loaded: document.fonts.check(style.font, copy),
      font_face_status: matchingFaces.length === 1 ? matchingFaces[0].status : "missing-or-ambiguous",
      measurement_method: measureContext ? "canvas-2d" : "unavailable",
      cap_height_ratio: measureContext && fontSize > 0 ? cap.actualBoundingBoxAscent / fontSize : null,
      word_width_ratio: measureContext && viewport.width > 0 ? measureContext.measureText(copy).width / viewport.width : null,
      line_count: lineHeight > 0 ? Math.round(rect.height / lineHeight) : 1,
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    };
  });
  const signatureElements = [...document.querySelectorAll("[data-continuity-signature]")].map((element) => {
    const rect = element.getBoundingClientRect();
    const roles = (element.getAttribute("data-continuity-signature-role") || "")
      .split(/\s+/)
      .map((value) => value.trim())
      .filter(Boolean);
    return {
      signature_id: element.getAttribute("data-continuity-signature"),
      roles,
      selector: selector(element),
      visible: visible(element),
      viewport_intersection_ratio: viewportIntersectionRatio(rect),
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    };
  });
  const interactionInvariants = [...document.querySelectorAll("[data-continuity-invariant]")].map((element) => {
    const style = getComputedStyle(element);
    return {
      invariant_id: element.getAttribute("data-continuity-invariant"),
      selector: selector(element),
      text: element.textContent.trim(),
      aria_label: element.getAttribute("aria-label"),
      aria_pressed: element.getAttribute("aria-pressed"),
      aria_selected: element.getAttribute("aria-selected"),
      disabled: Boolean(element.disabled),
      hidden: element.hidden || style.display === "none" || style.visibility === "hidden",
      value: "value" in element ? element.value : null,
    };
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
    if (measureContext) measureContext.font = style.font;
    const characterWidth = measureContext?.measureText("0").width;
    const characterMeasure = characterWidth ? rect.width / Math.max(characterWidth, 1) : null;
    if ((element.tagName === "P" || element.tagName === "LI") && lineCount >= 3 && characterMeasure !== null && characterMeasure > 75) {
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
  const presentationSlides = [...document.querySelectorAll("[data-continuity-slide]")].map((slide, slideIndex) => {
    const slideRect = slide.getBoundingClientRect();
    const textSelector = "h1, h2, h3, h4, p, li, dt, dd, blockquote, figcaption, th, td, [data-continuity-copy], [data-continuity-data]";
    const textElements = [...slide.querySelectorAll(textSelector)].filter((element) => {
      if (!element.textContent.trim()) return false;
      return ![...element.children].some((child) => child.matches?.(textSelector) && child.textContent.trim());
    });
    const issues = [];
    let copyCount = 0;
    let dataCount = 0;
    for (const element of textElements) {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      const isData = element.matches("th, td, [data-continuity-data]") || Boolean(element.closest("[data-continuity-data]"));
      if (isData) dataCount += 1;
      else copyCount += 1;
      const scaleX = element.offsetWidth > 0 ? rect.width / element.offsetWidth : 1;
      const scaleY = element.offsetHeight > 0 ? rect.height / element.offsetHeight : 1;
      const measuredScale = Math.min(scaleX || 1, scaleY || 1);
      const effectiveScale = Math.abs(measuredScale - 1) < 0.03 ? 1 : measuredScale;
      const effectiveFontSize = Number.parseFloat(style.fontSize) * effectiveScale;
      const title = element.matches("h1, h2, [data-continuity-slide-title]");
      const minimumFontSize = viewport.width >= 1200 ? (title ? 44 : isData ? 18 : 20) : (title ? 28 : 16);
      const insideSlide = rect.left >= slideRect.left - 1 && rect.top >= slideRect.top - 1 && rect.right <= slideRect.right + 1 && rect.bottom <= slideRect.bottom + 1;
      const clipsX = ["hidden", "clip", "auto", "scroll"].includes(style.overflowX);
      const clipsY = ["hidden", "clip", "auto", "scroll"].includes(style.overflowY);
      const clips = (clipsX && element.scrollWidth > element.clientWidth + 1) || (clipsY && element.scrollHeight > element.clientHeight + 1);
      const foreground = rgba(style.color);
      const background = opaqueBackground(element);
      const ratio = foreground && foreground.a >= 0.95 && background ? contrast(foreground, background) : null;
      const large = effectiveFontSize >= 24 || (effectiveFontSize >= 18.66 && (Number.parseInt(style.fontWeight, 10) || 400) >= 700);
      const minimumContrast = large ? 3 : 4.5;
      const elementIssues = [];
      if (!visible(element)) elementIssues.push("hidden");
      if (!insideSlide) elementIssues.push("outside-slide");
      if (clips) elementIssues.push("clipped");
      if (effectiveFontSize + 0.01 < minimumFontSize) elementIssues.push(`font-${effectiveFontSize.toFixed(1)}px-below-${minimumFontSize}px`);
      if (ratio !== null && ratio + 0.01 < minimumContrast) elementIssues.push(`contrast-${ratio.toFixed(2)}-below-${minimumContrast}`);
      if (document.fonts.status !== "loaded") elementIssues.push("fonts-not-loaded");
      if (elementIssues.length) {
        const item = { selector: selector(element), kind: isData ? "data" : "copy", issues: elementIssues };
        issues.push(item);
        add("presentation-copy-data-readability", "error", element, `${item.kind}: ${elementIssues.join(", ")}`);
      }
    }
    const copyReadable = copyCount > 0 && !issues.some((item) => item.kind === "copy");
    const dataReadable = !issues.some((item) => item.kind === "data");
    if (!copyCount) {
      issues.push({ selector: selector(slide), kind: "copy", issues: ["no-audience-facing-copy"] });
      add("presentation-copy-data-readability", "error", slide, "slide contains no audience-facing copy");
    }
    return {
      slide_id: slide.getAttribute("data-continuity-slide") || `slide-${slideIndex + 1}`,
      copy_element_count: copyCount,
      data_element_count: dataCount,
      copy_readable: copyReadable,
      data_readable: dataReadable,
      issues,
      rect: { x: slideRect.x, y: slideRect.y, width: slideRect.width, height: slideRect.height },
    };
  });
  const presentationReadabilityPassed = presentationSlides.length === 0 || presentationSlides.every((slide) => slide.copy_readable && slide.data_readable);
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
    schema_version: 3,
    probe_kind: "continuity-artifact-browser-probe",
    document_url: window.location.href,
    target_document_path: document.querySelector('meta[name="continuity-probe-target-path"]')?.content || null,
    target_document_sha256: document.querySelector('meta[name="continuity-probe-target-sha256"]')?.content || null,
    source_bundle_sha256: document.querySelector('meta[name="continuity-probe-source-bundle-sha256"]')?.content || null,
    viewport,
    document_fonts_status: document.fonts.status,
    media_preferences: { reduced_motion: window.matchMedia("(prefers-reduced-motion: reduce)").matches },
    composition_planes: compositionPlanes,
    typography_transfers: typographyTransfers,
    signature_elements: signatureElements,
    interaction_invariants: interactionInvariants,
    presentation_slides: presentationSlides,
    presentation_readability_passed: presentationReadabilityPassed,
    document: { scroll_width: root.scrollWidth, client_width: root.clientWidth },
    horizontal_overflow: horizontalOverflow,
    sticky_or_fixed_obstructions: obstructions,
    craft_findings: findings,
    passed: presentationReadabilityPassed && !horizontalOverflow && obstructions.length === 0 && !findings.some((item) => item.severity === "error" || item.severity === "critical"),
  };
})();
