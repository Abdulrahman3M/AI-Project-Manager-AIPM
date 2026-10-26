# RTL Hardening And Bilingual QA

Right alignment is **not** RTL. Arabic-first Word output is acceptable only when all applicable layers are set and the final artifact passes a structural audit plus an actual rendered-page review.

## Required DOCX layers

1. `word/settings.xml`: set `w:themeFontLang w:bidi` to the requested Arabic locale (for example `ar-EG`); this enables the complex-script language path used by Word.
2. `word/styles.xml`: set document-default run language `w:lang w:bidi`; set the default paragraph property to `w:bidi` and logical `w:jc w:val="start"`.
3. Each RTL section: add `w:bidi` in `w:sectPr` before `w:docGrid` when present.
4. Each semantic RTL table: add `w:bidiVisual` to `w:tblPr` so the first logical cell displays at the right. Do not reverse a table whose semantic order must remain LTR (for example source-code columns).
5. Each Arabic paragraph: add `w:bidi` and logical start alignment. A physical `right` alignment alone fails this requirement.
6. Each Arabic run: add `w:rtl` and complex-script language/font properties. Every English identifier, URL, DOI, path, formula and code span is an explicitly LTR run.

## Arabic-first text rules

- The Arabic paragraph establishes base direction. Keep `API`, `Python`, `C:\\Path`, `https://…`, DOIs, version strings, code and equations in isolated LTR runs; never reverse their characters by hand.
- Use Arabic punctuation naturally. For prose quotations, prefer `«…»` if the house style permits; a technical literal such as `هذا النص كمثال` uses the inline-code style only when it is actually a literal token/example.
- Do not insert bidirectional control characters as a cosmetic repair. Use them only for a documented edge case, record the reason, and add a regression sample.
- Keep numbers and citation markers visually checked after pagination. Do not assume renderer output proves Word Desktop behavior.

## Regression strings

Render and inspect each string in body text, a heading, a table cell, a callout, header/footer and a caption:

1. `هذه فقرة عربية تحتوي على API وPython وhttps://example.com/path?q=1.`
2. `استخدم الأمر: npm run build ثم راجع «النتيجة».`
3. `المثال: «النص العربي» (English note) [12].`
4. `الرمز المضمّن: هذا النص كمثال` with the literal token styled as `Code Inline`.

## Acceptance record

Record locale, builder/version, structural-audit result, renderer/version, Word Desktop status (PASS/FAIL/UNVERIFIED), every page inspected, and any exception. A passing OOXML audit means only that the tested layers exist; it does not guarantee identical behavior in every Word release, operating system, font set or printer.
