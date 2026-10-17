<!--
Version: 1.4.0
Type: Implementation Handoff Execution Prompt
Related Skill: create-strict-implementation-handoff
Updated: 2026-10-13
-->

Use the attached **Implementation Handoff** file as the strict and authoritative source of execution.
Apply `token-optimization` as independent lightweight support to reduce redundant reads or retries, never bypassing the handoff, governance, safety, or required tests.
For browser-relevant tasks, first verify an isolated AI browser with `browser-environment-manager`, use only owner-authorized startup/non-destructive repair, and ask before creating a new environment. If dedicated-browser use is refused or unavailable, try an authorized built-in Codex/cloud browser, then an authorized browser extension; never silently use a personal profile. Report unsupported browser checks `UNVERIFIED`. Default to one agent and never spawn subagents/multi-agent teams without explicit owner approval; preserve quality, tests and evidence.
Read it in full, then carry out all of its instructions and requirements in the exact order, scope, and level of precision specified within it, continuing through final verification and the closing report.
Do not replace implementation with analysis, discussion, or a proposed plan.
Do not consider the task complete unless and until all completion criteria, verification requirements, and final-status conditions defined in the **Implementation Handoff** have been fully satisfied.

<!-- The Prompt in Arabic Language -->

استخدم ملف **تسليم مرحلة التنفيذ (Implementation Handoff)** المرفق باعتباره المصدر المُلزِم والمرجعي للتنفيذ.
استخدم token-optimization كمهارة مساندة مستقلة دون الإخلال بالتعليمات أو الاختبارات أو معايير الجودة. في المهام التي تحتاج إلى متصفح، تحقق من بيئة AI مستقلة عبر browser-environment-manager؛ لا تنشئ بيئة جديدة دون إذن. عند الرفض أو التعذر استخدم المتصفح الداخلي المصرح به ثم إضافة المتصفح المصرح بها، دون فتح المتصفح الشخصي تلقائيًا؛ وسجّل الفحوصات غير الممكنة UNVERIFIED. استخدم وكيلاً واحدًا افتراضيًا ولا تشغّل Multi-Agent دون موافقة صريحة، مع الحفاظ على الدقة والجودة والاختبارات. اقرأ الملف بالكامل، ثم نفّذ جميع التعليمات والمتطلبات الواردة فيه ملتزماً بدقة بالترتيب والنطاق ومستوى الدقة المحددة داخله، مع المضي قدماً في الإجراءات حتى مرحلة التحقق النهائي وإعداد التقرير الختامي.
لا ​​تستبدل عملية التنفيذ بأي تحليلات أو مناقشات أو خطط مقترحة.
لا تُعتبر المهمة مُنجزة إلا بعد استيفاء كافة معايير الإنجاز، ومتطلبات التحقق، وشروط الحالة النهائية المحددة في ملف **تسليم مرحلة التنفيذ** بشكل كامل.
